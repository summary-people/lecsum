# 문제 생성 / 채점 프롬프트 템플릿
from langchain_core.prompts import ChatPromptTemplate

def get_quiz_prompt() -> ChatPromptTemplate:
    example_context = """
    객체 지향 프로그래밍(OOP)은 프로그램을 수많은 '객체(Object)'라는 기본 단위로 나누고 이들의 상호작용으로 로직을 구성하는 방식이다. 
    OOP의 4대 특징은 캡슐화, 상속, 다형성, 추상화이다.
    클래스(Class)는 객체를 만들기 위한 설계도이며, 인스턴스(Instance)는 그 설계도에 따라 실제 메모리에 생성된 실체를 의미한다.
    상속을 통해 부모 클래스의 속성과 메서드를 자식 클래스가 물려받아 재사용성을 높일 수 있다.
    """
    
    example_output = """
    {{
        "quizzes": [
            {{
                "type": "multiple_choice",
                "question": "다음 중 객체 지향 프로그래밍(OOP)의 4대 특징에 포함되지 않는 것은?",
                "options": ["캡슐화", "상속", "절차지향", "다형성"],
                "correct_answer": "절차지향",
                "explanation": "OOP의 4대 특징은 캡슐화, 상속, 다형성, 추상화입니다. 절차지향은 OOP와 대비되는 프로그래밍 패러다임입니다."
            }},
            {{
                "type": "true_false",
                "question": "Java의 Garbage Collector는 개발자가 직접 메모리를 해제해야 작동한다.",
                "options": ["O", "X"],
                "correct_answer": "X",
                "explanation": "Java는 GC가 자동으로 사용하지 않는 메모리를 해제해줍니다."
            }},
            {{
                "type": "fill_in_blank",
                "question": "부모 클래스의 기능을 자식 클래스가 물려받아 사용하는 개념을 _____ 이라고 한다.",
                "options": [],
                "correct_answer": "상속",
                "explanation": "상속(Inheritance)을 사용하면 코드의 재사용성을 높이고 유지보수를 용이하게 할 수 있습니다."
            }},
            {{
                "type": "multiple_choice",
                "question": "클래스와 인스턴스에 대한 설명으로 올바른 것은?",
                "options": [
                    "클래스는 실제로 메모리에 할당된 실체다.",
                    "하나의 클래스로는 하나의 인스턴스만 만들 수 있다.",
                    "인스턴스는 설계도이고 클래스는 실체다.",
                    "인스턴스는 클래스를 바탕으로 구현된 구체적인 실체다."
                ],
                "correct_answer": "인스턴스는 클래스를 바탕으로 구현된 구체적인 실체다.",
                "explanation": "클래스는 추상적인 설계도이고, 인스턴스는 그 설계도를 바탕으로 실제 메모리에 구현된 것입니다."
            }},
            {{
                "type": "short_answer",
                "question": "OOP에서 '객체'란 무엇을 의미하는가?",
                "options": [],
                "correct_answer": "프로그램의 기본 단위이자 로직을 구성하는 주체",
                "explanation": "객체는 데이터와 기능을 하나로 묶은 단위로, 객체 간의 상호작용을 통해 프로그램이 동작합니다."
            }}
        ]
    }}
    """

    return ChatPromptTemplate.from_messages([
        ("system", """
        당신은 베테랑 강사다. 주어진 [강의 내용]을 꼼꼼히 분석하여 학생들의 이해도를 평가할 수 있는 퀴즈를 5개 생성해라.
         
        [문제 유형 가이드]
        1. **multiple_choice**: 4지 선다형. 정답 1개.
        2. **true_false**: 사실 관계를 묻는 O/X 퀴즈.
        3. **short_answer**: 핵심 용어나 개념을 묻는 단답형.
        4. **fill_in_blank**: 문맥상 들어갈 알맞은 단어를 채우는 빈칸 채우기.

        [지시사항]
        1. **내용 선정**: 강의 내용 중 학습자가 반드시 알아야 할 핵심 개념(Key Concepts) 위주로 문제를 출제해라.
        2. **유형 배분**: 위 [문제 유형 가이드]의 4가지 유형을 모두 최소 1문제씩 포함하여 다양하게 구성해라.
        3. **오답 구성**: 오답(Distractor)은 정답과 헷갈릴 수 있는 매력적인 내용이어야 한다.
        4. **해설 작성**: 정답인 이유와 오답인 이유를 명확히 설명해라.
        """),
        # Few-shot
        ("human", f"강의 내용: {example_context}"),
        ("ai", example_output),

        # 실제 요청
        ("human", "강의 내용: {context}"),
    ])

def get_grading_prompt() -> ChatPromptTemplate:
    example_input = """
    다음 5개의 퀴즈 답안을 채점해줘.

    [문제 1]
    - 유형: short_answer
    - 문제: 자바 소스 코드를 컴파일하면 생성되는 중간 코드는 무엇인가?
    - 실제 정답: 바이트코드
    - 기존 해설: 자바 컴파일러는 소스(.java)를 JVM이 이해할 수 있는 바이트코드(.class)로 변환합니다.
    - 사용자 답: Byte Code

    [문제 2]
    - 유형: fill_in_blank
    - 문제: 데이터베이스에서 중복을 허용하지 않는 유일한 키를 _____ (이)라고 한다.
    - 실제 정답: 기본키
    - 기존 해설: 기본키(Primary Key)는 테이블 내에서 각 행을 식별하는 고유한 값입니다.
    - 사용자 답: 외래키

    [문제 3]
    - 유형: short_answer
    - 문제: OOP의 특징 중 하나로, 구현 세부 사항을 숨기고 인터페이스만 제공하는 것을 무엇이라 하는가?
    - 실제 정답: 캡슐화
    - 기존 해설: 캡슐화는 데이터와 메서드를 하나로 묶고 외부에서의 접근을 제어하여 정보 은닉을 수행합니다.
    - 사용자 답: 캡슐화는 정보를 은닉하는 것입니다.

    [문제 4]
    - 유형: short_answer
    - 문제: 웹 브라우저와 서버 간의 통신을 위해 사용되는 프로토콜의 약자는?
    - 실제 정답: HTTP
    - 기존 해설: HyperText Transfer Protocol의 약자로, 웹에서 데이터를 주고받는 규칙입니다.
    - 사용자 답: http

    [문제 5]
    - 유형: multiple_choice
    - 문제: 다음 중 스택(Stack) 자료구조의 특징으로 올바른 것은?
    - 실제 정답: LIFO (Last In First Out)
    - 기존 해설: 스택은 나중에 들어온 데이터가 먼저 나가는 후입선출 구조입니다.
    - 사용자 답: FIFO (First In First Out)
    """

    example_output = """
    {{
        "results": [
            {{
                "is_correct": true,
                "feedback": "정답입니다! \\n\\n해설: 한글 '바이트코드' 대신 영문 'Byte Code'로 적어주셨지만, 의미가 정확하므로 정답으로 인정됩니다. JVM이 이해하는 중간 단계 코드입니다."
            }},
            {{
                "is_correct": false,
                "feedback": "아쉽게도 틀렸습니다. 정답은 '기본키'입니다. \\n\\n해설: 작성하신 '외래키(Foreign Key)'는 다른 테이블을 참조할 때 사용하는 키입니다. 유일성을 보장하는 것은 '기본키'입니다."
            }},
            {{
                "is_correct": true,
                "feedback": "정답입니다! \\n\\n해설: 서술형으로 작성해주셨지만, 핵심 키워드인 '캡슐화'가 포함되어 있고 설명 또한 정확합니다."
            }},
            {{
                "is_correct": true,
                "feedback": "정답입니다! \\n\\n해설: 대소문자 구분 없이 'http'도 정답으로 인정됩니다. 웹 통신의 기본이 되는 프로토콜입니다."
            }},
            {{
                "is_correct": false,
                "feedback": "틀렸습니다. 정답은 'LIFO'입니다. \\n\\n해설: 선택하신 FIFO는 큐(Queue)의 특징입니다. 스택은 '후입선출(Last In First Out)' 구조라는 점을 기억해주세요!"
            }}
        ]
    }}
    """
    return ChatPromptTemplate.from_messages([
        ("system", """
        당신은 친절하고 정확한 AI 튜터다. 사용자가 제출한 5개의 퀴즈 답안을 채점해야 한다.

        [채점 기준]
        **단답형(short_answer) / 빈칸 채우기(fill_in_blank)**:
           - **유연한 채점(Fuzzy Matching)**을 적용해라.
           - 오타, 띄어쓰기 차이, 대소문자 차이는 무시하고 정답으로 인정해라.
           - 핵심 의미가 통하는 동의어도 정답으로 인정해라. (예: '객체 지향' == '객체지향 프로그래밍')
           - 사용자가 문장으로 답하더라도 핵심 키워드가 포함되어 있으면 정답으로 간주해라.

        [피드백 가이드]
        - **정답일 때**: 칭찬과 함께 기존 해설(explanation)을 요약해서 덧붙여라.
        - **오답일 때**: "아쉽네요, 틀렸습니다." 같은 말보다는, 왜 틀렸는지 설명하고 정답이 무엇인지 기존 해설을 바탕으로 친절하게 설명해라.
        - 한국어로 자연스럽게 작성해라.
        """),

        # Few-shot
        ("human", example_input),
        ("ai", example_output),

        # 실제 요청
        ("human", "{formatted_quiz_block}")       
    ])