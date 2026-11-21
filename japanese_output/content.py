"""Built-in content so the app works offline: the topic tree (R2/R3) and grammar list (R4).

Each topic's prompts follow the R3 chain: describe -> story -> opinion -> other side.
Every prompt is a (Japanese, English) pair.
"""

TOPICS = [
    # tier 0: the root
    {
        "id": "self_intro", "title": "自己紹介 Self introduction", "tier": 0, "requires": [],
        "prompts": {
            "describe": ("自分について紹介してください。名前、出身、仕事や学校など。",
                         "Introduce yourself: name, hometown, work or school."),
            "story": ("日本語を勉強し始めたきっかけを話してください。",
                      "Tell the story of how you started learning Japanese."),
            "opinion": ("自己紹介で一番大切なことは何だと思いますか。",
                        "What do you think matters most in a self introduction?"),
            "other_side": ("自己紹介は短い方がいいという意見に反論してください。",
                           "Argue against the idea that introductions should be short."),
        },
    },
    # tier 1: the trunk
    {
        "id": "daily_life", "title": "日常生活 Daily life", "tier": 1, "requires": ["self_intro"],
        "prompts": {
            "describe": ("あなたの普通の一日を説明してください。", "Describe a normal day for you."),
            "story": ("最近あった面白い出来事を話してください。",
                      "Tell a story about something interesting that happened recently."),
            "opinion": ("朝型と夜型、どちらがいいと思いますか。なぜですか。",
                        "Morning person or night owl: which is better, and why?"),
            "other_side": ("あなたと反対のタイプの人の立場で話してください。",
                           "Argue for the opposite type from your answer."),
        },
    },
    # tier 2: branches
    {
        "id": "work", "title": "仕事 Work", "tier": 2, "requires": ["daily_life"],
        "prompts": {
            "describe": ("あなたの仕事（または将来したい仕事）を説明してください。",
                         "Describe your job (or the job you want)."),
            "story": ("仕事や学校で大変だった日のことを話してください。",
                      "Tell about a hard day at work or school."),
            "opinion": ("在宅勤務についてどう思いますか。", "What do you think of working from home?"),
            "other_side": ("オフィスで働く方がいいという立場で話してください。",
                           "Argue that working in an office is better."),
        },
    },
    {
        "id": "travel", "title": "旅行 Travel", "tier": 2, "requires": ["daily_life"],
        "prompts": {
            "describe": ("行ったことがある場所を一つ説明してください。", "Describe a place you have been."),
            "story": ("旅行中に起きたハプニングを話してください。",
                      "Tell about something unexpected on a trip."),
            "opinion": ("一人旅と友達との旅行、どちらが好きですか。",
                        "Solo travel or travel with friends: which do you prefer?"),
            "other_side": ("あなたが選ばなかった方の良さを話してください。",
                           "Make the case for the option you did not pick."),
        },
    },
    {
        "id": "anime_manga", "title": "アニメ・漫画 Anime & manga", "tier": 2,
        "requires": ["daily_life"],
        "prompts": {
            "describe": ("好きなアニメか漫画を説明してください。", "Describe an anime or manga you like."),
            "story": ("その作品の好きな場面のあらすじを話してください。",
                      "Retell your favorite scene from it."),
            "opinion": ("アニメは大人も見るべきだと思いますか。", "Should adults watch anime?"),
            "other_side": ("アニメは子供向けだという人の立場で話してください。",
                           "Argue the side of someone who says anime is for kids."),
        },
    },
    {
        "id": "food", "title": "食べ物 Food", "tier": 2, "requires": ["daily_life"],
        "prompts": {
            "describe": ("好きな料理と作り方を説明してください。", "Describe a dish you like and how it is made."),
            "story": ("忘れられない食事について話してください。", "Tell about a meal you will never forget."),
            "opinion": ("外食と自炊、どちらがいいと思いますか。", "Eating out or cooking at home: which is better?"),
            "other_side": ("反対の意見を持つ人の立場で話してください。", "Argue the opposite view."),
        },
    },
    {
        "id": "hobbies", "title": "趣味 Hobbies", "tier": 2, "requires": ["daily_life"],
        "prompts": {
            "describe": ("あなたの趣味を説明してください。", "Describe your hobby."),
            "story": ("その趣味を始めた時の話をしてください。", "Tell how you got into it."),
            "opinion": ("趣味にお金をかけるべきだと思いますか。", "Is it worth spending money on hobbies?"),
            "other_side": ("趣味は時間の無駄だという意見を説明してください。",
                           "Argue that hobbies are a waste of time."),
        },
    },
    # tier 3: deeper topics under each branch
    {
        "id": "career", "title": "キャリア Career goals", "tier": 3, "requires": ["work"],
        "prompts": {
            "describe": ("十年後の自分のキャリアを説明してください。", "Describe your career ten years from now."),
            "story": ("仕事について大きな決断をした時の話をしてください。",
                      "Tell about a big decision you made about work or study."),
            "opinion": ("一つの会社でずっと働くことをどう思いますか。",
                        "What do you think of staying at one company for life?"),
            "other_side": ("転職を繰り返す人の立場で話してください。",
                           "Argue for changing jobs often."),
        },
    },
    {
        "id": "travel_stories", "title": "旅の思い出 Travel stories", "tier": 3,
        "requires": ["travel"],
        "prompts": {
            "describe": ("いつか住んでみたい国を説明してください。", "Describe a country you would like to live in."),
            "story": ("旅行で出会った人の話をしてください。", "Tell about someone you met while traveling."),
            "opinion": ("観光地が観光客でいっぱいになる問題をどう思いますか。",
                        "What do you think about overtourism?"),
            "other_side": ("観光客が増えることの良さを話してください。",
                           "Argue that more tourists is a good thing."),
        },
    },
    {
        "id": "stories_media", "title": "物語とキャラ Stories & characters", "tier": 3,
        "requires": ["anime_manga"],
        "prompts": {
            "describe": ("好きなキャラクターの性格を説明してください。", "Describe a favorite character's personality."),
            "story": ("もしそのキャラクターに会えたら、どんな一日になるか話してください。",
                      "Tell the story of a day spent with that character."),
            "opinion": ("いい物語に必要なものは何だと思いますか。", "What does a good story need?"),
            "other_side": ("ハッピーエンドは良くないという立場で話してください。",
                           "Argue that happy endings are bad."),
        },
    },
    {
        "id": "food_culture", "title": "食文化 Food culture", "tier": 3, "requires": ["food"],
        "prompts": {
            "describe": ("あなたの国の食文化を説明してください。", "Describe the food culture where you live."),
            "story": ("初めて食べて驚いた料理の話をしてください。", "Tell about a food that surprised you."),
            "opinion": ("ファストフードが増えることをどう思いますか。", "What do you think of fast food spreading?"),
            "other_side": ("ファストフードを擁護してください。", "Defend fast food."),
        },
    },
    {
        "id": "learning", "title": "学ぶこと Learning skills", "tier": 3, "requires": ["hobbies"],
        "prompts": {
            "describe": ("あなたの勉強方法を説明してください。", "Describe how you study."),
            "story": ("何かが上手になった経験を話してください。", "Tell about getting good at something."),
            "opinion": ("才能と努力、どちらが大切だと思いますか。", "Talent or effort: which matters more?"),
            "other_side": ("あなたと反対の意見を説明してください。", "Argue the opposite of your answer."),
        },
    },
    # tier 4: abstract
    {
        "id": "opinions_society", "title": "社会と意見 Opinions & society", "tier": 4,
        "requires": ["career", "learning", "stories_media"],
        "prompts": {
            "describe": ("最近気になっている社会問題を説明してください。",
                         "Describe a social issue on your mind lately."),
            "story": ("その問題があなたの生活に影響した話をしてください。",
                      "Tell how that issue has affected your life."),
            "opinion": ("その問題はどうすれば解決できると思いますか。", "How could it be solved?"),
            "other_side": ("あなたの解決策に反対する人の立場で話してください。",
                           "Argue against your own solution."),
        },
    },
    {
        "id": "culture_compare", "title": "文化比較 Culture comparison", "tier": 4,
        "requires": ["travel_stories", "food_culture", "stories_media"],
        "prompts": {
            "describe": ("日本とあなたの国の違いを一つ説明してください。",
                         "Describe one difference between Japan and your country."),
            "story": ("文化の違いで困った経験を話してください。", "Tell about a culture clash you experienced."),
            "opinion": ("外国に住むとき、その国の文化に合わせるべきですか。",
                        "When living abroad, should you adapt to the local culture?"),
            "other_side": ("自分の文化を守るべきだという立場で話してください。",
                           "Argue for keeping your own culture."),
        },
    },
    {
        "id": "technology", "title": "技術と未来 Technology & the future", "tier": 4,
        "requires": ["career", "learning"],
        "prompts": {
            "describe": ("あなたの生活を変えた技術を説明してください。", "Describe a technology that changed your life."),
            "story": ("スマホがなかった頃の思い出を話してください。", "Tell about life before smartphones."),
            "opinion": ("AIは人の仕事を奪うと思いますか。", "Will AI take people's jobs?"),
            "other_side": ("反対の立場で話してください。", "Argue the opposite side."),
        },
    },
    # tier 5: philosophy
    {
        "id": "happiness", "title": "幸せとは What is happiness", "tier": 5,
        "requires": ["opinions_society", "culture_compare"],
        "prompts": {
            "describe": ("あなたにとっての幸せを説明してください。", "Describe what happiness means to you."),
            "story": ("一番幸せだった瞬間を話してください。", "Tell about your happiest moment."),
            "opinion": ("お金で幸せは買えると思いますか。", "Can money buy happiness?"),
            "other_side": ("あなたと反対の意見を説得力を持って話してください。",
                           "Argue the opposite convincingly."),
        },
    },
    {
        "id": "meaning_work", "title": "働く意味 Work & meaning", "tier": 5,
        "requires": ["technology", "opinions_society"],
        "prompts": {
            "describe": ("人はなぜ働くのか、あなたの考えを説明してください。", "Explain why you think people work."),
            "story": ("仕事や勉強にやりがいを感じた時の話をしてください。",
                      "Tell about a time work or study felt meaningful."),
            "opinion": ("働かなくてもいい社会は良い社会だと思いますか。",
                        "Would a society where no one has to work be good?"),
            "other_side": ("反対の立場で話してください。", "Argue the opposite side."),
        },
    },
]

RETELLING_PROMPTS = {
    "summarize": ("読んだ・聞いたものを一分でまとめてください。",
                  "Summarize what you read or listened to in about a minute."),
    "details": ("一番印象に残った部分を詳しく話してください。",
                "Retell the part that stuck with you most, in detail."),
    "reaction": ("それについてどう思いましたか。賛成ですか、反対ですか。",
                 "What did you think of it? Do you agree or disagree?"),
    "other_side": ("作者や話し手と反対の立場で話してください。",
                   "Argue against the author or speaker."),
}

# Grammar points in teaching order, tagged by JLPT level.
GRAMMAR = [
    # N5
    {"id": "n5_masu", "level": "N5", "pattern": "〜ます / 〜ません", "meaning": "polite verb (positive/negative)",
     "example": "毎朝コーヒーを飲みます。"},
    {"id": "n5_tai", "level": "N5", "pattern": "〜たい", "meaning": "want to do",
     "example": "日本に行きたいです。"},
    {"id": "n5_te_kudasai", "level": "N5", "pattern": "〜てください", "meaning": "please do",
     "example": "ゆっくり話してください。"},
    {"id": "n5_ta_koto", "level": "N5", "pattern": "〜たことがある", "meaning": "have done before",
     "example": "寿司を作ったことがあります。"},
    {"id": "n5_kara", "level": "N5", "pattern": "〜から", "meaning": "because",
     "example": "雨だから、家にいます。"},
    {"id": "n5_tari", "level": "N5", "pattern": "〜たり〜たりする", "meaning": "do things like A and B",
     "example": "週末は本を読んだり映画を見たりします。"},
    # N4
    {"id": "n4_tsumori", "level": "N4", "pattern": "〜つもり", "meaning": "plan / intend to",
     "example": "来年引っ越すつもりです。"},
    {"id": "n4_to_omou", "level": "N4", "pattern": "〜と思う", "meaning": "I think that",
     "example": "この映画は面白いと思います。"},
    {"id": "n4_tara", "level": "N4", "pattern": "〜たら", "meaning": "if / when",
     "example": "時間があったら、遊びに来てください。"},
    {"id": "n4_nagara", "level": "N4", "pattern": "〜ながら", "meaning": "while doing",
     "example": "音楽を聞きながら勉強します。"},
    {"id": "n4_sou", "level": "N4", "pattern": "〜そうだ (look)", "meaning": "looks like",
     "example": "このケーキはおいしそうです。"},
    {"id": "n4_noni", "level": "N4", "pattern": "〜のに", "meaning": "even though",
     "example": "勉強したのに、忘れてしまった。"},
    # N3
    {"id": "n3_you_ni_naru", "level": "N3", "pattern": "〜ようになる", "meaning": "come to be able to / start to",
     "example": "日本語が話せるようになりました。"},
    {"id": "n3_wake_dewa_nai", "level": "N3", "pattern": "〜わけではない", "meaning": "it's not that",
     "example": "嫌いなわけではありません。"},
    {"id": "n3_ni_yoruto", "level": "N3", "pattern": "〜によると", "meaning": "according to",
     "example": "ニュースによると、明日は雪です。"},
    {"id": "n3_koto_ni_suru", "level": "N3", "pattern": "〜ことにする", "meaning": "decide to",
     "example": "毎日日記を書くことにしました。"},
    {"id": "n3_ba_hodo", "level": "N3", "pattern": "〜ば〜ほど", "meaning": "the more ... the more",
     "example": "練習すればするほど上手になる。"},
    # N2
    {"id": "n2_ni_kanshite", "level": "N2", "pattern": "〜に関して", "meaning": "regarding",
     "example": "この問題に関して意見があります。"},
    {"id": "n2_ni_chigainai", "level": "N2", "pattern": "〜に違いない", "meaning": "must be / no doubt",
     "example": "彼は疲れているに違いない。"},
    {"id": "n2_mono_no", "level": "N2", "pattern": "〜ものの", "meaning": "although",
     "example": "買ったものの、まだ使っていない。"},
    {"id": "n2_ue_de", "level": "N2", "pattern": "〜上で", "meaning": "upon / in doing",
     "example": "仕事を選ぶ上で、給料は大切だ。"},
    {"id": "n2_kaneru", "level": "N2", "pattern": "〜かねる", "meaning": "cannot (politely)",
     "example": "その意見には賛成しかねます。"},
    # N1
    {"id": "n1_ni_hokanaranai", "level": "N1", "pattern": "〜にほかならない", "meaning": "nothing but",
     "example": "成功は努力の結果にほかならない。"},
    {"id": "n1_to_wa_ie", "level": "N1", "pattern": "〜とはいえ", "meaning": "that said / although",
     "example": "春とはいえ、まだ寒い。"},
    {"id": "n1_mai", "level": "N1", "pattern": "〜まい", "meaning": "will not / probably not",
     "example": "二度と同じ失敗はするまい。"},
    {"id": "n1_ni_soku_shite", "level": "N1", "pattern": "〜に即して", "meaning": "in line with",
     "example": "事実に即して話してください。"},
    {"id": "n1_wo_kawakiri_ni", "level": "N1", "pattern": "〜を皮切りに", "meaning": "starting with",
     "example": "東京を皮切りに、全国でツアーをする。"},
]
