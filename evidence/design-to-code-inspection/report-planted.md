# Design-to-code inspection: index.html

50 measurements at 375, 768, 1280 px; **10 mismatches**. Tolerance ±2px.

| Width | Check | Expected | Measured | |
|---:|---|---|---|---|
| 375 | no-horizontal-scroll | scrollWidth <= viewport | 1px overflow | **MISMATCH** |
| 375 | card-mobile:box.x | 16px ±2 | 16px | ok |
| 375 | card-mobile:box.width | 343px ±2 | 360px | **MISMATCH** |
| 375 | plan-name:style.font-size | 28px | 28px | ok |
| 375 | plan-name:style.font-weight | 700 | 700 | ok |
| 375 | plan-name:style.color | #1d1d1b | rgb(29, 29, 27) | ok |
| 375 | plan-name:text | contains "Studio" | Studio | ok |
| 375 | price:style.font-size | 40px | 40px | ok |
| 375 | price:style.color | #1d1d1b | rgb(29, 29, 27) | ok |
| 375 | features:count | 3 | 3 | ok |
| 375 | cta:style.border-radius | 10px | 10px | ok |
| 375 | cta:style.color | #ffffff | rgb(255, 255, 255) | ok |
| 375 | cta:style.background-color | #2f5bea | rgb(47, 91, 234) | ok |
| 375 | cta:target-size | >= 44px | 304x36 | **MISMATCH** |
| 375 | fine-print:visible | true | true | ok |
| 375 | fine-print:style.font-size | 14px | 12px | **MISMATCH** |
| 768 | no-horizontal-scroll | scrollWidth <= viewport | 0px overflow | ok |
| 768 | card:box.width | 360px ±2 | 360px | ok |
| 768 | card:style.border-radius | 12px | 8px | **MISMATCH** |
| 768 | card:style.background-color | #ffffff | rgb(255, 255, 255) | ok |
| 768 | plan-name:style.font-size | 28px | 28px | ok |
| 768 | plan-name:style.font-weight | 700 | 700 | ok |
| 768 | plan-name:style.color | #1d1d1b | rgb(29, 29, 27) | ok |
| 768 | plan-name:text | contains "Studio" | Studio | ok |
| 768 | price:style.font-size | 40px | 40px | ok |
| 768 | price:style.color | #1d1d1b | rgb(29, 29, 27) | ok |
| 768 | features:count | 3 | 3 | ok |
| 768 | cta:style.border-radius | 10px | 10px | ok |
| 768 | cta:style.color | #ffffff | rgb(255, 255, 255) | ok |
| 768 | cta:style.background-color | #2f5bea | rgb(47, 91, 234) | ok |
| 768 | cta:target-size | >= 44px | 304x36 | **MISMATCH** |
| 768 | fine-print:visible | true | true | ok |
| 768 | fine-print:style.font-size | 14px | 12px | **MISMATCH** |
| 1280 | no-horizontal-scroll | scrollWidth <= viewport | 0px overflow | ok |
| 1280 | card:box.width | 360px ±2 | 360px | ok |
| 1280 | card:style.border-radius | 12px | 8px | **MISMATCH** |
| 1280 | card:style.background-color | #ffffff | rgb(255, 255, 255) | ok |
| 1280 | plan-name:style.font-size | 28px | 28px | ok |
| 1280 | plan-name:style.font-weight | 700 | 700 | ok |
| 1280 | plan-name:style.color | #1d1d1b | rgb(29, 29, 27) | ok |
| 1280 | plan-name:text | contains "Studio" | Studio | ok |
| 1280 | price:style.font-size | 40px | 40px | ok |
| 1280 | price:style.color | #1d1d1b | rgb(29, 29, 27) | ok |
| 1280 | features:count | 3 | 3 | ok |
| 1280 | cta:style.border-radius | 10px | 10px | ok |
| 1280 | cta:style.color | #ffffff | rgb(255, 255, 255) | ok |
| 1280 | cta:style.background-color | #2f5bea | rgb(47, 91, 234) | ok |
| 1280 | cta:target-size | >= 44px | 304x36 | **MISMATCH** |
| 1280 | fine-print:visible | true | true | ok |
| 1280 | fine-print:style.font-size | 14px | 12px | **MISMATCH** |

Screenshots: [375](shot-375.png), [768](shot-768.png), [1280](shot-1280.png)

Measured values only. Look at the screenshots before deciding which mismatches matter.
