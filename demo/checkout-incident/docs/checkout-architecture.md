# Checkout payment flow

`storefront → checkout-api.submit_payment → normalize_currency → payment-service.create_charge → gateway`

The storefront may send locale-qualified values such as `usd-us`. The checkout boundary owns conversion to the gateway contract. `create_charge` accepts ISO-4217 alpha-3 currency values. Inventory reservation and gateway health are independent of the conversion step.

