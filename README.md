# Sarcophagus × Certora Verification Suite

Welcome 👋  
This repository contains:

1. **Sarcophagus** — a decentralized *Dead‑Man’s‑Switch* protocol written in Solidity.  
2. **Certora specs & configs** that formally verify core safety properties.

---

## 1  What the Sarcophagus contract does

> “*…uses Ethereum as the source‑of‑truth, Arweave for encrypted storage, and a
> decentralized network of secret‑holders (“archaeologists”) who reveal a
> private key only if the embalmer stops checking‑in.*” — `Sarcophagus.sol`

### Key roles

| Role | Responsibility |
|------|----------------|
| **Embalmer** | Creates a sarcophagus, pays fees, can extend/cancel/bury it. |
| **Archaeologist** | Locks a bond, guards the secret key, earns fees/bounty if they behave. |
| **Recipient** | Gets the secret once the switch triggers. |
| **SARCO token** | ERC‑20 used for all fees, bounties and bonds. |

### Lifecycle (happy‑path)

1. **createSarcophagus** – embalmer chooses an archaeologist, sets resurrection time & fees.  
2. **updateSarcophagus** – embalmer uploads encrypted payload to Arweave and posts its `assetId`.  
3. **rewrapSarcophagus** – optional extension of resurrection time.  
4. **unwrapSarcophagus** – anyone can call after the deadline with the archaeologist’s key → funds are settled.  
5. Optional escape hatches: **cancel**, **bury**, **cleanUp**, **accuseArchaeologist**.

All heavy logic lives in libraries (`Archaeologists.sol`, `Sarcophaguses.sol`, `Utils.sol`, …); the main contract is a thin proxy façade.

---

## 2  Why Certora? What we check

Certora Prover symbolically executes the EVM byte‑code and proves that **every
possible execution** obeys the rules we state.  
No fuzzing, no test vectors—*mathematical guarantees*.

### Our campaign

* **Config:** `certora/conf/sarcophagus.conf`  
  * single target file (`contracts/Sarcophagus.sol`)  
  * IR pipeline + optimizer enabled  
* **Spec:** `certora/specs/sarcophagus.spec`  
  * **11 rules** (single‑trace properties)  
  * **1 invariant** (holds across all traces)

### Highlighted properties

| # | Rule / Invariant | What it guarantees |
|---|------------------|--------------------|
| 1 | **`registerIncreasesCount`** | Registering an archaeologist never reduces `archaeologistCount()`. |
| 2 | **`registerReturnsValidIndex`** | The index returned by `registerArchaeologist` equals the previous length. |
| 3 | **`updateDoesNotChangeCount`** | Updating a profile cannot create or delete archaeologists. |
| 4 | **`withdrawDoesNotChangeCount`** | Bond withdrawals don’t affect the global count. |
| 5 | **`createIncreasesSarcophagusCount`** | Creating a sarcophagus can only increase (or keep) the total count. |
| 7–10 | **cancel/rewrap/bury/cleanup** rules | None of those ops are allowed to *increase* the sarcophagus counter. |
| 11 | **`nonZeroArchaeologistAddress`** | Stored archaeologist addresses are never the zero address. |
| — | **Invariant `validArchaeologistArray`** | *For every block*: every index `< archaeologistCount()` holds a non‑zero address. |

Implementation tricks:

* **Bootstrap helpers** create a dummy archaeologist & sarcophagus so we don’t operate on empty state.
* Dynamic data (`string`, `bytes`) is capped to stay within Certora’s default `--hashing_length_bound = 224` bytes → no “unbounded hashing” errors.

---

## 3  Running the proofs locally

```bash
# install once
pip install certora-cli --upgrade

# run campaign
certoraRun certora/conf/sarcophagus.conf