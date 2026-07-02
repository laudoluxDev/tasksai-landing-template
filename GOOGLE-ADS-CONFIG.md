# Google Ads Configuration

Google Analytics is configured per vertical with `ga_measurement_id`.

Google Ads tracking is optional. Add these fields to a vertical in `verticals.json` only when that vertical has its own Google Ads account and conversion labels:

```json
{
  "google_ads_id": "AW-XXXXXXXXXX",
  "google_ads_signup_conversion_label": "signupLabel",
  "google_ads_checkout_conversion_label": "checkoutLabel",
  "google_ads_purchase_conversion_label": "purchaseLabel"
}
```

When `google_ads_id` is present, the generated Google tag config includes both the GA4 measurement ID and the Ads ID. When a conversion label is also present, generated pages emit Ads conversion events for that action:

- `signup.html`: completed signup or waitlist form
- `index.html` and `buy-credits.html`: checkout started before redirecting to Stripe
- `success.html`: purchase confirmation

Missing Ads fields are safe. The pages still emit GA4 events where applicable, but they do not send Google Ads conversions.
