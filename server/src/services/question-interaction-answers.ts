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
  return parsePaperclipQuestionResponse(questionSet, response);
}

