# Cookbook-Task

install requirements\
`pip3 install -r requirements.txt`

### Endpoints

| Endpoint name  | Function |
| ------------- | ------------- |
| `/login`  | Basic auth request, returns token |
| `/verify-token`  | Information if token is valid (requires {'token': <valid_token>} in header) |
| `/ingredient` | List of ingredients (token) |
| `/recipe` | List of recipes (token)|
| `/recipe/<recipe_id>` | Recipe details (token)|
