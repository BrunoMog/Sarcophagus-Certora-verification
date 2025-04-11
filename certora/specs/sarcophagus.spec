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
//  Rules (≥10)                                                   
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

// ─────────────────────────────────────────────────────────────
//  Invariant: every index < archaeologistCount() holds a non‑zero address
// ─────────────────────────────────────────────────────────────
invariant validArchaeologistArray(uint256 i)
    i < archaeologistCount() => archaeologistAddresses(i) != 0x0000000000000000000000000000000000000000;