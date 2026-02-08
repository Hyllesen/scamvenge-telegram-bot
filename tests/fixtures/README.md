# Test Fixtures

This directory should contain sample "Store Follow" screenshots for integration testing.

## Adding Test Images

1. **Collect Screenshots**: Gather 5-10 real "Store Follow" screenshots from Telegram
2. **Name Files Descriptively**: Use format `storename_keyword.jpg`
   - Example: `nike_following.jpg`
   - Example: `adidas_sold.jpg`
   - Example: `theshop_items.jpg`

3. **Expected Results**: Update the `EXPECTED_RESULTS` dictionary in `test_integration.py`:
   ```python
   EXPECTED_RESULTS = {
       'nike_following.jpg': 'Nike Store',
       'adidas_sold.jpg': 'Adidas',
       'theshop_items.jpg': 'The Shop',
   }
   ```

## Image Requirements

- **Format**: JPG or PNG
- **Content**: Must contain at least one of these keywords:
  - "Following"
  - "Sold"
  - "Items"
- **Quality**: Clear, readable text
- **Store Name**: Should be the largest/most prominent text

## Testing Without Fixtures

If you don't have sample images yet, the integration tests will be skipped automatically. The unit tests (which use mocked data) will still run.

## Example Structure

```
fixtures/
├── README.md (this file)
├── nike_following.jpg
├── adidas_sold.jpg
├── puma_items.jpg
└── theshop_following.jpg
```
