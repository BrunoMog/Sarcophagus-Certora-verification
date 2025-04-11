// ─────────────────────────────────────────────────────────────
//  Method block – expose every public/view fn we’ll touch
// ─────────────────────────────────────────────────────────────
methods {
    /* views */
    function archaeologistCount() external returns uint256 envfree;
    function archaeologistAddresses(uint256) external returns address envfree;
    function sarcophagusCount()     external returns uint256 envfree;

    /* mutating calls we exercise in the rules */
    function registerArchaeologist(
        bytes     currentPublicKey,
        string    endpoint,
        address   paymentAddress,
        uint256   feePerByte,
        uint256   minimumBounty,
        uint256   minimumDiggingFee,
        uint256   maximumResurrectionTime,
        uint256   freeBond
    ) external returns uint256;

    function updateArchaeologist(
        string    endpoint,
        bytes     newPublicKey,
        address   paymentAddress,
        uint256   feePerByte,
        uint256   minimumBounty,
        uint256   minimumDiggingFee,
        uint256   maximumResurrectionTime,
        uint256   freeBond
    ) external returns bool;

    function withdrawBond(uint256) external returns bool;

    function createSarcophagus(
        string  name,
        address archaeologist,
        uint256 resurrectionTime,
        uint256 storageFee,
        uint256 diggingFee,
        uint256 bounty,
        bytes32 identifier,
        bytes   recipientPublicKey
    ) external returns uint256;

    function cancelSarcophagus(bytes32) external returns bool;
    function rewrapSarcophagus(bytes32,uint256,uint256,uint256) external returns bool;
    function burySarcophagus(bytes32) external returns bool;
    function cleanUpSarcophagus(bytes32,address) external returns bool;
}

// ─────────────────────────────────────────────────────────────
//  Helper: a single safe‑assumption used by several rules
// ─────────────────────────────────────────────────────────────
function nonReentrantSender(env e) {
    require(e.msg.sender != currentContract);   // ignore self‑calls
}

// ─────────────────────────────────────────────────────────────
//  Rules                                                    
// ─────────────────────────────────────────────────────────────

// 1. Registering must increase (or keep) the archaeologist count.
rule registerIncreasesCount(
    env e,
    bytes key,
    string endpoint,
    address payAddr,
    uint256 feePB,
    uint256 minB,
    uint256 minDF,
    uint256 maxRT,
    uint256 bond
){
    uint256 beforeCnt = archaeologistCount();
    registerArchaeologist(e,key,endpoint,payAddr,feePB,minB,minDF,maxRT,bond);
    uint256 afterCnt  = archaeologistCount();
    assert afterCnt >= beforeCnt, "archaeologistCount decreased after register";
}

// 2. Returned index from register == previous length.
rule registerReturnsValidIndex(
    env e,
    bytes key,
    string endpoint,
    address payAddr,
    uint256 feePB,
    uint256 minB,
    uint256 minDF,
    uint256 maxRT,
    uint256 bond
){
    uint256 beforeCnt = archaeologistCount();
    uint256 idx = registerArchaeologist(e,key,endpoint,payAddr,feePB,minB,minDF,maxRT,bond);
    assert idx == beforeCnt, "wrong index returned on register";
}

// 3. Updating profile must NOT change the total count.
rule updateDoesNotChangeCount(
    env e,
    string endpoint,
    bytes key,
    address payAddr,
    uint256 feePB,
    uint256 minB,
    uint256 minDF,
    uint256 maxRT,
    uint256 bond
){  
    registerArchaeologist(e,key,endpoint,payAddr,feePB,minB,minDF,maxRT,bond);
    uint256 beforeCnt = archaeologistCount();
    updateArchaeologist(e,endpoint,key,payAddr,feePB,minB,minDF,maxRT,bond);
    uint256 afterCnt  = archaeologistCount();
    assert afterCnt == beforeCnt, "update changed archaeologistCount";
}

// 4. Withdrawing bond must NOT change the total count.
rule withdrawDoesNotChangeCount(env e, uint256 amt){
    uint256 beforeCnt = archaeologistCount();
    withdrawBond(e,amt);
    uint256 afterCnt  = archaeologistCount();
    assert afterCnt == beforeCnt, "withdraw changed archaeologistCount";
}

// 5. Creating a sarcophagus increases (or keeps) the global count.
rule createIncreasesSarcophagusCount(
    env e,
    string  name,
    address arch,
    uint256 rTime,
    uint256 sFee,
    uint256 dFee,
    uint256 bounty,
    bytes32 id,
    bytes   recipKey
){
    require(name.length <= 32);
    require(recipKey.length <= 32);
    nonReentrantSender(e);
    uint256 beforeCnt = sarcophagusCount();
    createSarcophagus(e,name,arch,rTime,sFee,dFee,bounty,id,recipKey);
    uint256 afterCnt  = sarcophagusCount();
    assert afterCnt >= beforeCnt, "sarcophagusCount decreased after create";
}

// 6. Returned index from create == previous length.
rule createReturnsValidIndex(
    env e,
    string  name,
    address arch,
    uint256 rTime,
    uint256 sFee,
    uint256 dFee,
    uint256 bounty,
    bytes32 id,
    bytes   recipKey
){
    require(name.length <= 32);
    require(recipKey.length <= 32);
    uint256 beforeCnt = sarcophagusCount();
    uint256 idx = createSarcophagus(e,name,arch,rTime,sFee,dFee,bounty,id,recipKey);
    assert idx == beforeCnt, "wrong index returned on create";
}

// 7. Cancelling must NOT increase the sarcophagus count.
rule cancelDoesNotIncreaseCount(env e, bytes32 id){
    uint256 beforeCnt = sarcophagusCount();
    cancelSarcophagus(e,id);
    uint256 afterCnt  = sarcophagusCount();
    assert afterCnt <= beforeCnt, "cancel increased sarcophagusCount";
}

// 8. Rewrap must NOT increase the sarcophagus count.
rule rewrapDoesNotIncreaseCount(env e, bytes32 id, uint256 rTime, uint256 dFee, uint256 bounty){
    uint256 beforeCnt = sarcophagusCount();
    rewrapSarcophagus(e,id,rTime,dFee,bounty);
    uint256 afterCnt  = sarcophagusCount();
    assert afterCnt <= beforeCnt, "rewrap increased sarcophagusCount";
}

// 9. Bury must NOT increase the sarcophagus count.
rule buryDoesNotIncreaseCount(env e, bytes32 id){
    uint256 beforeCnt = sarcophagusCount();
    burySarcophagus(e,id);
    uint256 afterCnt  = sarcophagusCount();
    assert afterCnt <= beforeCnt, "bury increased sarcophagusCount";
}

// 10. Clean‑up must NOT increase the sarcophagus count.
rule cleanupDoesNotIncreaseCount(env e, bytes32 id, address payAddr){
    uint256 beforeCnt = sarcophagusCount();
    cleanUpSarcophagus(e,id,payAddr);
    uint256 afterCnt  = sarcophagusCount();
    assert afterCnt <= beforeCnt, "cleanUp increased sarcophagusCount";
}

// 11. Any stored archaeologist address must be non‑zero.
rule nonZeroArchaeologistAddress(uint256 idx){
    uint256 cnt = archaeologistCount();
    require(idx < cnt);
    assert archaeologistAddresses(idx) != 0x0000000000000000000000000000000000000000, "stored address is zero";
}

// ─────────────────────────────────────────────────────────────
//  Invariant: every index < archaeologistCount() holds a non‑zero address
// ─────────────────────────────────────────────────────────────
invariant validArchaeologistArray(uint256 i)
    i < archaeologistCount() => archaeologistAddresses(i) != 0x0000000000000000000000000000000000000000;