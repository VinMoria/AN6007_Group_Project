# API Document
## 1. User Register
**Description:** Register a new user, return the user id

**Endpoint:** /user/register

**Method:** POST

**Request Body:**

```json
{
    "username": "string",
    "area": "string"
}
```

**Response Body:**

```json
{
    "user_id": "string",
    "status": "success"
}
```

## 2. User Get Data
**Description:** Get the data of the user

**Endpoint:** /user/getData

**Method:** GET	

**Request Parameters:** user_id

**Response Body:**

```json
{
    "area": "Orchard Road",
    "day_usage_history": [
        14001
    ],
    "latest_day_usage": 17106,
    "latest_month_usage": 31107,
    "latest_week_usage": 17106,
    "month_usage_history": [],
    "status": "success",
    "user_id": "00000004",
    "username": "Diana White",
    "week_usage_history": [
        14001
    ]
}
```







