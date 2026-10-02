import type { AskUserQuestionsAnswer, AskUserQuestionsPayload, PaperclipQuestionSetPayload } from "@paperclipai/shared";
import { parsePaperclipQuestionResponse, type PaperclipQuestionResponse } from "../vendor/paperclip-runner/index.js";

/** Validate storage answers against the persisted canonical form before resolution. */
export function parseQuestionInteractionAnswers(
  questionSet: PaperclipQuestionSetPayload,
  answers: readonly AskUserQuestionsAnswer[],
  storageQuestions: AskUserQuestionsPayload["questions"],
): PaperclipQuestionResponse {
  const answerByQuestionId = new Map(answers.map((answer) => [answer.questionId, answer]));
  const response: PaperclipQuestionResponse = {
    schema: "paperclip.question_response.v1",
    answers: {},
  };
  for (const question of questionSet.questions) {
    const answer = answerByQuestionId.get(question.id);
    if (!answer) continue;
    if (question.answerMode === "text") {
      response.answers[question.id] = {
        ...(answer.otherText !== undefined && answer.otherText !== null
          ? { text: answer.otherText }
          : {}),
      };
    } else {
      const customOptionId = storageQuestions.find((entry) => entry.id === question.id)
        ?.options.find((option) => option.freeText)?.id ?? null;
      response.answers[question.id] = {
        selectedOptionIds: answer.optionIds.filter((optionId) => optionId !== customOptionId),
        ...(answer.otherText !== undefined && answer.otherText !== null
          ? { customText: answer.otherText }
          : {}),
      };
    }
  }
  // Historical dual forms may offer a written answer only in storage. Keep
  // that pending answer path usable; new creation rejects this mismatch.
  const answerableQuestionSet = {
    ...questionSet,
    questions: questionSet.questions.map((question) => {
      const storage = storageQuestions.find((entry) => entry.id === question.id);
      if (question.answerMode !== "text" && !question.customAnswer
        && (storage?.allowOther === true || storage?.options.some((option) => option.freeText))) {
        return { ...question, customAnswer: { enabled: true as const } };
      }
      return question;
    }),
  };
  return parsePaperclipQuestionResponse(answerableQuestionSet, response);
}
