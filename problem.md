# Problem

When learning japanese (or any language) most learners will spend almost all of there time on
input, reading, listening, doing flashcards, watching anime, etc. and almost no time actually
outputting. This leads to a situation where a learner can understand alot but when it comes
time to actually speak they freeze up and cant put a sentence together. The problem is that
output is uncomfortable and theres no clear way to practice it by yourself, you dont know what
to talk about, you run out of things to say after a couple minutes, and you have no way to know
if your getting better. Grammar also gets learned passively, you recognize it when you read it
but you never actually use it so it never sticks. That is why there needs to be something that
forces the learner to output everyday, gives them something to talk about, and makes it feel
rewarding to keep going.

# Initial requirements

- R1. The program asks the user for there current japanese level (beginner, N5, N4, N3, N2,
  N1) so that the user does not start from 0 if they already have experience, and the program
  saves it.
- R2. Topics should be layed out as a branching tree instead of a straight line (ex. self
  introduction -> daily life -> than branches into work, travel, anime/manga, etc.). Topics
  start simple and expand out into harder and more abstract topics (opinions, culture,
  philosophy, etc.). The users level from R1 decides where on the tree they start, and the
  user can choose which branch to unlock next.
- R3. The program everyday gives the user a topic from the tree. Each topic should be broken
  up into prompts that build on each other so the user doesnt run out of things to say,
  describe it -> tell a story about it -> give your opinion -> argue the other side. Some days
  should be a retelling task instead, where the user retells something they read or listened
  to (an interview, article, etc.) in there own words.
- R4. The program should everyday introduce a couple new grammar points that the user has to
  try and use while talking. Grammar points the user has already learned should come back
  using SRS so the user keeps using them and does not forget.
- R5. The program should have a timer for the speaking session and record the user so they
  can listen back to what they said. The minimum session is 10-15mins to keep the streak
  alive, but the user can keep going up to 1 hour for bonus xp.
- R6. The program should be gamified, the user should earn xp for minutes spoken, grammar
  points used, and new words added, have a streak for how many days in a row they outputted,
  and level up to unlock new branches of the topic tree. It should feel like a game and not
  like homework
