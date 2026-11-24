# 課題: 別ユーザーのリクエスト制限が互いに影響し合う

`throttle/limiter.ts` の `RateLimiter.allow(userId)` は、ユーザーごとに1分あたり5回まで
リクエストを許可するトークンバケット方式のレート制限です。運用チームから次の不具合報告が
ありました。

## 再現手順

```ts
import { RateLimiter } from "./throttle/limiter.ts";

const limiter = new RateLimiter();
limiter.allow("alice"); // true
limiter.allow("alice"); // true
limiter.allow("alice"); // true (これで alice は3回消費)

// bob は今回が初めてのリクエストのはずなので、5回とも true になるべき
console.log(limiter.allow("bob")); // true になるべき
console.log(limiter.allow("bob")); // true になるべき
console.log(limiter.allow("bob")); // true になるべき
console.log(limiter.allow("bob")); // true になるべき
console.log(limiter.allow("bob")); // true になるべき
console.log(limiter.allow("bob")); // false になるべき（6回目）
```

しかし実際には、**bob は3回目のリクエストで早くも `false` を返してしまいます**
（alice が消費した分がなぜか bob にも影響しているように見える）。1人のユーザーが
上限に達するまで連続でリクエストするだけの既存テスト（`tests/limiter.test.ts`）は、
この「複数ユーザー間の相互影響」を検出できていません。

## 求めること

- 上記の再現手順の通り、各ユーザーが独立して自分専用の5回分の残高を持つように修正してください。
- 原因を `throttle/limiter.ts` の残高判定・消費ロジック自体に限定して探さないこと。
  1人のユーザーだけを使う既存テストは正しく通っており、上限判定・消費の計算式自体に誤りはありません。

## 制約

- `tests/limiter.test.ts` は既存のテストです。実装がこれを壊さないようにしてください。
- `throttle/bucket.ts` のデータ構造（`Bucket` インターフェースと `createBucket`）は変更しないでください。
- 外部ライブラリは使用しないこと。
