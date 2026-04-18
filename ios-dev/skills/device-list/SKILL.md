---
name: device-list
description: Use this skill when the user wants to check connected physical iOS/iPadOS devices for building or testing on a real device. Trigger on phrases like "実機ビルド", "実機確認", "実機で動作確認", "実機デバイス一覧", "接続デバイス確認", "list physical devices", "connected devices", "build to device", "real device build", "run on device". Always use this skill when the user mentions wanting to use a physical device (not Simulator) for building, testing, or debugging.
context: fork
---

# List Physical iOS Devices

接続されている実機デバイスを一覧表示し、`xcodebuild` の `-destination` に使える文字列を提示する。

## Purpose

- USB/ネットワーク接続されたiOS/iPadOSデバイスの一覧取得
- `xcodebuild -destination` に指定する文字列の確認
- デバイスのUDID・OS バージョンの確認

## Workflow

1. `xcrun xctrace list devices` で実機デバイスを取得
2. `== Devices ==` セクションのみ抽出（Simulatorセクションは除外）
3. Mac自体（macOSエントリ）を除いたiOS/iPadOSデバイスのみ表示
4. 各デバイスの destination 文字列を提示

## Command

```bash
xcrun xctrace list devices
```

出力の `== Devices ==` セクションに実機デバイスが列挙される。`== Simulators ==` 以降はシミュレータなので無視する。

### デバイスのみ抽出（Mac除く）

```bash
xcrun xctrace list devices 2>/dev/null | awk '/^== Devices ==/{found=1; next} /^== Simulators ==/{found=0} found && NF'
```

出力例:
```
MacBook Pro M5 (D29C93FE-E17B-5B1C-8020-65A5F156D0EA)
iPhone 17 Pro Max (26.4.1) (00008150-000A404621F0401C)
```

Mac（MacBook / iMac / Mac mini など）はiOSビルドの destination としては使わないので、iOS/iPadOS デバイスのみをユーザーに提示すること。

## Output Format

ユーザーへの提示形式（各デバイスについて）:

```
デバイス名: iPhone 17 Pro Max
iOS バージョン: 26.4.1
UDID: 00008150-000A404621F0401C

destination 文字列:
  特定デバイス指定: platform=iOS,id=00008150-000A404621F0401C
  デバイス名指定:   platform=iOS,name=iPhone 17 Pro Max
```

## xcodebuild での使い方

```bash
xcodebuild build \
  -workspace MyApp.xcworkspace \
  -scheme MyApp \
  -destination 'platform=iOS,id=<UDID>'
```

**汎用的な実機 destination（接続デバイスがあれば自動選択）:**
```
generic/platform=iOS
```

> Note: `generic/platform=iOS` は接続デバイスを自動選択するが、コード署名の設定が必要。

## デバイスが見つからない場合

デバイスが表示されない場合の確認ポイント:
1. USBケーブルで接続されているか
2. デバイス側で「このコンピュータを信頼」が承認済みか
3. Xcodeで「Devices and Simulators」(⇧⌘2) を開いてデバイスが認識されているか
4. `xcrun devicectl list devices` でも確認可能（Xcode 15以降）

## build-app スキルとの連携

実機 destination を確認したら、`build-app` スキルを使ってビルドを実行する:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/build-app/scripts/build.py \
    --project ./MyApp.xcworkspace \
    --scheme MyApp \
    --destination "platform=iOS,id=<UDID>"
```
