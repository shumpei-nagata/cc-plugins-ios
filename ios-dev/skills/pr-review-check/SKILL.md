---
name: pr-review-check
description: Use this skill when the user wants to "PRのレビューコメントを確認", "レビュー内容を評価して", "指摘の妥当性を見て", "どのコメントに対応すべきか", "PRのフィードバックを整理", "レビューが来たので確認したい", "指摘を優先順位付けして", "pr review", "check pr comments", or any similar request to review, evaluate, or prioritize comments and feedback on a GitHub PR. Fetches all PR comments (inline code review threads, review bodies, and general issue comments) using gh CLI and GraphQL, then evaluates each for technical validity, scope, and importance — including iOS/Swift-specific concerns. Always use this skill proactively when the user mentions reviewing PR feedback, checking review comments, or figuring out what to fix in a PR.
---

# PR レビューコメント評価

PRについたすべてのコメントを取得し、技術的妥当性・スコープ適切性・重要度を評価して一覧表示する。

## Step 1: PRの特定

現在のブランチに紐づくPRを自動検出する:

```bash
gh pr view --json number,title,url,headRefName 2>/dev/null
```

- 取得できた場合: PR番号・タイトルをユーザーに確認してから続行する
- 取得できなかった場合: 「対象のPR番号を教えてください」とユーザーに確認する

## Step 2: リポジトリ情報の取得

```bash
gh repo view --json owner,name
```

owner と name を取得し、後続のAPIコールで使う。

## Step 3: コメントの収集（GraphQL）

GraphQL APIを使い、1回のクエリですべての情報を取得する:

```bash
gh api graphql -f query='
query($owner: String!, $repo: String!, $number: Int!) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $number) {
      number
      title
      body
      url
      reviewThreads(first: 100) {
        nodes {
          isResolved
          isOutdated
          comments(first: 50) {
            nodes {
              id
              url
              author { login }
              authorAssociation
              body
              path
              line
              originalLine
              diffHunk
              createdAt
            }
          }
        }
      }
      reviews(first: 100) {
        nodes {
          id
          url
          author { login }
          authorAssociation
          state
          body
          createdAt
        }
      }
      comments(first: 100) {
        nodes {
          id
          url
          author { login }
          authorAssociation
          body
          createdAt
        }
      }
    }
  }
}' \
-F owner=OWNER -F repo=REPO -F number=NUMBER
```

### データの整理

取得したデータを以下の3種類に分類する:

1. **reviewThreads**: インラインコードコメントのスレッド群。各スレッドは1つ以上のコメントを持ち、最初のコメントが指摘本体、2件目以降は返信。`isResolved` でスレッドの解決状態がわかる。
2. **reviews**: レビュー本文（APPROVED / CHANGES_REQUESTED / COMMENTED 等のステータス付き）。bodyが空の場合はスキップ。
3. **comments**: PRスレッドへの一般コメント（issueコメント）。

空のbody（空文字・空白のみ）はスキップする。

## Step 4: コンテキストの参照

評価の精度を上げるため、以下を読み込む:

```bash
# プロジェクトルールの確認
[ -f CLAUDE.md ] && cat CLAUDE.md
find .claude -name "*.md" -o -name "rules" 2>/dev/null | head -5 | xargs cat 2>/dev/null

# PRの差分概要（スコープ判断に使う）
gh pr diff --name-only 2>/dev/null || gh pr view {number} --json files --jq '[.files[].path]'
```

## Step 5: 各コメントの評価

収集したすべてのコメントについて、以下の基準で評価する。

### 妥当性 (validity)

コメントの技術的正確性と、このPRのスコープへの適合性を判断する:

| ラベル | 意味 |
|--------|------|
| `妥当` | 技術的に正しく、このPRの変更範囲で対応すべき指摘 |
| `別タスク` | 指摘の内容は正しいが、このPRのスコープ外。別途対応が望ましい |
| `スコープ外` | このPRの変更と直接関係しない |
| `要確認` | 正誤の判断にコンテキストが不足しているか、作者の意図確認が必要 |
| `不妥当` | 技術的に誤り、または誤解に基づく指摘 |
| `-` | LGTM・承認コメント・スレッドの返信など評価対象外 |

### 重要度 (priority)

一般的なコードレビューの重要度基準で判断する:

| レベル | 基準 |
|--------|------|
| `Critical` | バグ・セキュリティ脆弱性・クラッシュリスク・データ破損・ビルド不可 |
| `High` | パフォーマンス問題・設計上の重大な懸念・ロジックの誤り・リグレッション |
| `Medium` | 可読性・保守性・ベストプラクティス違反・テスト不足 |
| `Low` | 軽微な改善提案・スタイル・命名・個人の好みの範囲 |
| `-` | 評価対象外（承認のみ等） |

### iOS/Swift 固有の判断観点

diff_hunk や指摘内容に以下が含まれる場合、重要度を判断する際の参考にする:

- メインスレッドでのAPI呼び出し・重い処理（`viewDidLoad`での同期処理等）→ Critical/High
- 強参照サイクル（`[weak self]`・`[unowned self]`の漏れ）→ High
- SwiftUI/UIKitのライフサイクル違反 → High
- `force unwrap`（`!`）の不適切な使用 → Medium〜High（コンテキストによる）
- `@MainActor`・`async/await`の誤用 → High
- メモリ管理の問題（`retain cycle`・不要な強参照）→ High
- Swift API Design Guidelines違反 → Medium/Low
- `print`文の残留 → Low
- Xcodeのwarningに相当する指摘 → Medium

### Botコメントの扱い

`authorAssociation` や login名（`[bot]`サフィックス等）からbotを識別する。Copilot・Codexなどのbotコメントも一覧に含めるが、出力の「投稿者」列に `🤖` を付けて区別する。botの指摘は人間レビュワーと同様に妥当性・重要度を評価するが、誤検知・過検知が多い傾向を考慮してやや慎重に評価する。

### スレッド評価の注意点

インラインコメントはスレッド単位で評価する。スレッド内に複数コメントがある場合（指摘→返信→合意など）、スレッド全体の文脈を読んだ上で妥当性を判断する。返信のみのコメントは個別評価しない。

## Step 6: 結果の出力

以下の形式でMarkdownとして出力する:

### サマリー

```
## PRレビューコメント評価: {PR title} (#{number})
{url}

### サマリー
- コメント総数: {n}件（reviewThreads: {n} / reviews: {n} / comments: {n}）
- 🔴 Critical: {n}件  🟠 High: {n}件  🟡 Medium: {n}件  🟢 Low: {n}件
- このPRで対応推奨（妥当）: {n}件
- 別タスク推奨: {n}件
- スキップ可能（スコープ外・不妥当・解決済み）: {n}件
```

### コメント一覧

テーブル形式で出力する。見やすさのため重要度の高い順に並べる（Critical → High → Medium → Low → 評価対象外）:

```
| # | タイプ | 投稿者 | 場所 | コメント概要 | 妥当性 | 重要度 | 判断理由 |
|---|--------|--------|------|------------|--------|--------|---------|
```

各列の説明:
- **タイプ**: `inline`（コードコメント）/ `review`（レビュー本文）/ `comment`（一般コメント）
- **投稿者**: login名。botには `🤖` プレフィックス
- **場所**: inlineは `ファイル名:行番号`（ファイル名は末尾部分のみ）、それ以外は `-`
- **コメント概要**: 50〜60文字程度に要約。元のURLリンクを付ける（`[概要](url)`）
- **妥当性**: 上記ラベルの1つ
- **重要度**: 上記レベルの1つ。`解決済み`の場合はその旨を付記
- **判断理由**: 1〜2文で根拠を示す

### 対応推奨リスト（オプション）

Critical/Highで妥当性が「妥当」のコメントが3件以上ある場合、末尾に優先対応リストを追加する:

```
### 優先対応リスト
1. [Critical] {コメント概要} → {URL}
2. [High] ...
```
