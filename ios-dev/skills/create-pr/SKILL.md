---
name: create-pr
description: Use this skill when the user wants to "create a pull request", "open a PR", "submit a PR", "PRを作成", "プルリクエストを作成", "PRを出す", "GitHubにPRを上げる", "レビューを依頼する", or any similar request to push work to GitHub for review. Creates a PR using the gh CLI, auto-generates the body from git log (respecting .github/PULL_REQUEST_TEMPLATE.md if present), and automatically requests reviews from both GitHub Copilot and Codex. Use this skill proactively whenever the user's intent is clearly to create a GitHub PR, even if they don't explicitly say "PR" — for example, "作業終わったのでレビューしてもらいたい" or "マージしてほしいのでレビュー依頼したい".
context: fork
---

# GitHub PR Creator

GitHubにPull Requestを作成し、CopilotとCodexの両方にレビューを自動依頼するワークフロー。

## ワークフロー

### Step 1: git状態の確認

現在のブランチと未コミットの変更を確認する:

```bash
git status --short
git branch --show-current
```

- 未コミットの変更がある場合 → ユーザーに警告して続行確認
- `main` / `master` ブランチにいる場合 → フィーチャーブランチへの切り替えを促して停止

### Step 2: ベースブランチの確認

リポジトリのデフォルトブランチを取得してユーザーに確認:

```bash
gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name'
```

「ベースブランチは `<default>` でよいですか？」と確認する。

### Step 3: PRタイトルの決定

ベースブランチからのコミット一覧を取得してタイトル候補を生成:

```bash
git log --oneline origin/<base>..HEAD
```

- コミットが1件 → そのコミットメッセージをタイトル候補にする
- コミットが複数 → ブランチ名や変更の主旨を要約してタイトル候補を提示

候補をユーザーに提示し、確認または修正を求める。

### Step 4: PR本文の生成

まずPRテンプレートの有無を確認:

```bash
[ -f .github/PULL_REQUEST_TEMPLATE.md ] && cat .github/PULL_REQUEST_TEMPLATE.md
```

コミット履歴と差分サマリーを取得:

```bash
git log origin/<base>..HEAD --format="%s%n%b"
git diff origin/<base>..HEAD --stat
```

**テンプレートが存在する場合**: テンプレートの各セクションをコミット情報をもとに埋める。空白のままにするセクションは残す。

**テンプレートがない場合**: 以下の構成で本文を生成する:

```
## Summary
（このPRで何をしたか、1〜3行で）

## Changes
- （主な変更点をboxリストで）

## Test plan
- （動作確認の手順）
```

生成した本文をユーザーに提示し、確認を取ってから次に進む。

### Step 5: PRの作成

確認が取れたらPRを作成。`--reviewer @copilot` を付けてCopilotレビューを同時に依頼する:

```bash
gh pr create \
  --base <base-branch> \
  --title "<title>" \
  --body "<body>" \
  --reviewer @copilot
```

**フォールバック**: `@copilot` がレビュアーとして無効（リポジトリでCopilotが有効でない等）でエラーになった場合は、`--reviewer @copilot` を外してPRを作成し、その後以下で追加する:

```bash
gh pr edit --add-reviewer @copilot
```

### Step 6: Codexレビューの依頼

PR作成後にコメントを投稿してCodexのレビューをトリガーする:

```bash
gh pr comment --body "@codex review"
```

### Step 7: 完了報告

以下を出力する:
- PR URL
- Copilotレビュー依頼済みの確認
- Codexレビューコメント投稿済みの確認
