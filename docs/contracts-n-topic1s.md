## GMX Contracts

- See [this master list of GMX contract addresses for both chains](https://github.com/gmx-io/gmx-interface/blob/master/src/Addresses.js).

## Topic1s

Topic1s are chain agnostic.

### General Topic1s (not GMX specific)

- Transfer: '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
- Claim   : '0x47cee97cb7acd717b3c0aa1435d004cd5b3c8c57d70dbceb4e4458bbd60e39d4'

### GMX-specific Topic1s

under GlpManager:

- AddLiquidity: '0x38dc38b96482be64113daffd8d464ebda93e856b70ccfc605e69ccf892ab981e'
- RemoveLiquidity: '0x87b9679bb9a4944bafa98c267e7cd4a00ab29fed48afdefae25f0fca5da27940'

under RewardRouter:

- StakeGlp:   '0xa4725d47fa458d9222498e4d63f34527cf7318c1506f89d9092b35fdbcb64f3a'
- UnstakeGlp: '0x1cb6202519b6b6c72ba5ed11e2c3f53af3cea010f96bfc705584e53e75cf034c'
- StakeGmx:   '0x277a108bb56dcaa99fe060708d8fdf34a9ad95c3f857452c0a2621154ec90b78'
- UnstakeGmx: '0xe9da6f830e88eb523af6d57c34cc795daaafe1ab891b6ec4f276a550532124a5'

under RewardRouterV2:

- StakeGlp:   '0xa4725d47fa458d9222498e4d63f34527cf7318c1506f89d9092b35fdbcb64f3a'
- UnstakeGlp: '0x1cb6202519b6b6c72ba5ed11e2c3f53af3cea010f96bfc705584e53e75cf034c'
- StakeGmx:   '0xad0723806aa1e5a8fb826fc9f0c5b589e585a6b60dc768a1b20691c95062d2d6'
- UnstakeGmx: '0xce8eb393006add0768cc6cefb3ca0fc4787015ce1ac86bd800e72a7999310345'

under Vault: (there are 21 of them; we list 4 for now)

- IncreaseUsdgAmount: '0x64243679a443432e2293343b77d411ff6144370404618f00ca0d2025d9ca9882'
- DecreaseUsdgAmount: '0xe1e812596aac93a06ecc4ca627014d18e30f5c33b825160cc9d5c0ba61e45227'
- Swap:               '0x0874b2d545cb271cdbda4e093020c452328b24af12382ed62c4d00f5c26709db'
- BuyUSDG:            '0xab4c77c74cd32c85f35416cf03e7ce9e2d4387f7b7f2c1f4bf53daaecf8ea72d'

for getting platform revenue:

- CollectSwapFees  :  '0x47cd9dda0e50ce30bcaaacd0488452b596221c07ac402a581cfae4d3933cac2b'
- CollectMarginFees:  '0x5d0c0019d3d45fadeb74eff9d2c9924d146d000ac6bcf3c28bf0ac3c9baa011a'