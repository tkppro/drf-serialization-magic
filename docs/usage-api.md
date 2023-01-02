## Base Parameters

### Reference

**`serializer_cls`**`(serializers.BaseSerializer|str)` <br>
The serializer class to use 

**`paginator`**`(Optional)` <br>
Default will use pagination in settings file
```api_settings.DEFAULT_PAGINATION_CLASS()```

**`error_messages`**`(Optional[str])` <br>
Error message

## ValidateSerialization

### Reference

**`location`**`(str)` <br>
The location to validate data(body or header)

**`to_key`**`(Optional[str])` <br>
Can be used to pass a custom key for validated data dict
