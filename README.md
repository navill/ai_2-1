# AI project - Back-End





### Tech

- Language: Python(3.7)

- Database: MongoDB(MongoDB server version 4.2.7)

### requirements

- Django == 3.0
- Django REST Framework == 3.11.1
- Django REST Framework - SimpleJWT == 4.4.0
- djongo == 1.3.3





### JWT with Logout

- 기존의 JWT의 경우 완전한 logout 기능을 제공하지 않음
  - blacklist를 이용하여 사용자의 접근을 제한하지만, 접근 토큰의 유효기간이 만료되지 않은 상태라면 언제든 접근 가능 - logout을 해도 접근이 가능한 문제

1. logout 시, blacklist(redis)에 {'username': 'jti'} 를 저장(jti: JWT에 포함된 비식별 값)
2. 해당 토큰을 이용해 접근할 경우 redis에 동일한 jti값이 올라가 있기 때문에 접근이 불가
   - sliding token이 refresh되어도 jti는 변경되지 않기 때문에 만료시간 또는 로그아웃 전까지 접근이 허용됨
   - 로그아웃이 될 경우, 토큰의 만료 시간이 유지되어도 접근을 제한함