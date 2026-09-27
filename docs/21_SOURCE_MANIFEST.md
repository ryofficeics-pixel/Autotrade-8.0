# 21 — Source Manifest

## Purpose

Identify the exact non-document sources used to form the AUTOTRADE 8.0 design. Identical filenames do not imply identical content.

## Repository artifacts

| File | Bytes | SHA-256 | Classification |
|---|---:|---|---|
| `Screenshot_20260924-182739_Threads.png` | 514,698 | `f8779eede04b2b141bd79fc85fd0ce94d12cdad69c186ac674a366757a360cec` | social-media claim/inspiration only |
| `Screenshot_20260924-182743_Threads.png` | 511,591 | `cb59e9a9ad6036768cc0446ab9ec92532a71db92818881bc3f188d442357d2c3` | social-media claim/inspiration only |
| `Screenshot_20260924-182746_Threads.png` | 347,319 | `7ef65c3697c79ef79921645f30085454b837f59ff44641f6826540e4cd6bee10` | social-media claim/inspiration only |
| `Screenshot_20260924-182750_Threads.png` | 472,874 | `a55ffd972d82fa866757fac9586540e213bb0594d95b10e5d43fa249a5661543` | social-media claim/inspiration only |
| `Screenshot_20260924-182756_Threads.png` | 431,463 | `417ef8b47fc4aa12c8a9178585d02f1b4589e9ae6d739da9bc1de7c8aa65c234` | social-media claim/inspiration only |
| `Screenshot_20260924-182759_Threads.png` | 369,536 | `5fe57c119da0c4af3e758d16f02a2fdf56ea8990946d746a16eaf8ff7db71c5b` | social-media comments; no alpha evidence |
| `Screenshot_20260924-184050_Threads.png` | 1,050,351 | `2ff4ce86bf14e994ead517e825c1c81dec50d8437a81ae92694ae38273e8f112` | TensorTrade/RL reference |
| `Screenshot_20260924-184056_Threads.png` | 871,285 | `0819e3736b6f5998f8cc55b2f6230b9596ab946d90f9fb2a0b903293e17767fb` | TensorTrade/RL reference |
| `Screenshot_20260924-184159_Threads.png` | 609,089 | `6a31375e3485027be210ea6bdd97f4fda9d6d2f162f2d3a99a71b19258f1a993` | indicator idea; unvalidated |
| `autotrade8_phase1.zip` | 44,131 | `3df6ea830e53764c66b64aaa1f8e5fa1d2efe6718c5e05b77d12f2d58ff0b68d` | archived prototype/reference only |

## Separately supplied artifact

The discussion also inspected a separately supplied file with the same visible base name:

| Source | Bytes | SHA-256 | Observation |
|---|---:|---|---|
| uploaded `autotrade8_phase1.zip` | 16,032 | `ec0676dba9940fda5babbcd1824c6f422f036f17e77e07d83491d6d79b05c394` | older/smaller prototype; differs from repository ZIP |

The separately supplied ZIP is not added to the repository because that would create ambiguous duplicate provenance.

## Trust classification

- `EVIDENCE`: immutable measured/logged result with provenance.
- `REFERENCE`: code or concept requiring independent validation.
- `CLAIM`: unverifiable external assertion; never used for promotion.

All screenshots are `CLAIM` or `REFERENCE`. The Phase 1 ZIPs are `REFERENCE`. None is an approved runtime artifact.

## Update rule

When a source artifact changes, add a new manifest row/version. Do not replace its hash or rewrite history. A later artifact with the same filename must be renamed or versioned explicitly.
