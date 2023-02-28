# 냥랭 (Nyanlang)

세상에서 제일 귀여운 언어다냥!  
당연히 Brainfxxk 기반인건 알고 가라냥!

[위키](https://github.com/sserve-kr/Nyanlang/wiki)도 있다냥!!

아래는 비교 표다냥.


| Brainfxxk | Nyanlang | Description                     |
|-----------|----------|---------------------------------|
| >         | ?        | 포인터 증가                          |
| <         | !        | 포인터 감소                          |
| +         | 냥        | 포인터가 가리키는 바이트의 값 증가             |
| -         | 냐        | 포인터가 가리키는 바이트의 값 감소             |
| .         | .        | 포인터가 가리키는 바이트의 값을 ASCII로 출력     |
| ,         | ,        | 포인터가 가리키는 바이트에 ASCII 값 입력       |
| [         | ~        | 포인터가 가리키는 바이트의 값이 0이 아닐 때까지 반복  |
| ]         | -        | 포인터가 가리키는 바이트의 값이 0이 될 때까지 반복   |
| X         | 뀨        | (디버깅용) 포인터가 가리키는 바이트의 값을 그대로 출력 |

주석도 지원한다냥!

주석은 `"` 문자로 감싸서 쓰면 된다냥.

```
" 주석 - 이 부분은 인터프리터가 무시할 거다냥! 인터프리터 바-보 "
냥냥냥.
```

# 코드 포맷팅
이렇게 귀여운 코드지만 조금 더 귀엽게 하기 위해 몇 가지 규칙들을 만들어 봣다냥!  
이 규칙들은 지키든 안지키든 상관 없지만냥, 가급적이면 이 언어의 목적에 맞는 
**"귀여움"** 에 부합하기 위해서라도 써줬으면 좋겠다냥!

귀여움을 강조하는 규칙들은 다음과 같다냥!
1. `?`나 `!` 문자 뒤에는 띄어쓰기를 해야 한다냥! 예를 들면 다음과 같다냥.
    + `냥냥냥냥? 냥냥냥냥냥`
    + `냥냥냥냥냥~? 냥냥`
    + `냥!!!!! 냐-? 냐`
2. `?`나 `!` 이외의 문자들의 뒤가 `?`나 `!`로 끝나면 띄어쓰기를 하지 않는게 좋다냥.
    + `냥냥냥냥냥~?`
    + `냥냥..!`
3. 그런데 `?`나 `!` 이외의 문자들의 뒤가 `냥`이나 `냐`라면 띄어쓰기를 하는게 좋다냥!
    + `냥냥냥냥냥~ 냥냥.! 냐-`
    + `냥냥..! 냐-? 냐`
4. `냥`이나 `냐`가 너무 길어지면 5개 단위로 끊는게 좋다냥.
    + `냥냥냥냥냥 냥냥냥냥~`
    + `냐냐냐냐냐 냐!`

# 예제

아래는 냥랭으로 쓴 Hello World 코드 예제다냥!

Brainfxxk과 비교해보면 더 귀여워 보일거다냥!

```
냥냥냥냥냥 냥냥냥냥냥~? 냥냥냥냥냥 냥냥? 냥냥냥냥냥 냥냥냥냥냥? 냥냥냥? 냥!!!! 냐-? 냥냥.? 냥. 냥냥냥냥냥 냥냥..
냥냥냥.? 냥냥냥냥냥 냥냥냥냥냥 냥냥냥냥. 냐냐냐냐냐 냐냐냐냐냐 냐냐.!! 냥냥냥냥냥 냥냥냥냥냥 냥냥냥냥냥.? . 냥냥냥. 냐냐냐냐냐 냐. 냐냐냐냐냐 냐냐냐.? 냥.
```