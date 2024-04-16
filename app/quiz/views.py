from aiohttp.web_exceptions import HTTPConflict, HTTPNotFound, HTTPBadRequest
from aiohttp_apispec import request_schema, response_schema, querystring_schema

from app.quiz.models import Answer
from app.quiz.schemes import (
    ThemeSchema, ThemeListSchema, QuestionSchema, ThemeIdSchema, ListQuestionSchema,
)
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


class ThemeAddView(AuthRequiredMixin, View):
    @request_schema(ThemeSchema)
    @response_schema(ThemeSchema)
    async def post(self):
        title = self.data["title"]
        check_theme = await self.store.quizzes.get_theme_by_title(title=title)
        if not check_theme:
            theme = await self.store.quizzes.create_theme(title=title)
            return json_response(data=ThemeSchema().dump(theme))
        raise HTTPConflict


class ThemeListView(AuthRequiredMixin, View):
    @response_schema(ThemeListSchema)
    async def get(self):
        themes = await self.request.app.store.quizzes.list_themes()
        raw_themes = [ThemeSchema().dump(obj=theme) for theme in themes]
        return json_response(data={"themes": raw_themes})


class QuestionAddView(AuthRequiredMixin, View):
    @request_schema(QuestionSchema)
    @response_schema(QuestionSchema, 200)
    async def post(self):
        title = self.data["title"]
        theme_id = self.data["theme_id"]
        answers = [Answer.from_dict(answer) for answer in self.data["answers"]]
        question = await self.store.quizzes.create_question(title=title, theme_id=theme_id, answers=answers)
        return json_response(data=QuestionSchema().dump(question))


class QuestionListView(AuthRequiredMixin, View):
    @querystring_schema(ThemeIdSchema)
    @response_schema(ListQuestionSchema)
    async def get(self):
        questions = await self.store.quizzes.list_questions(theme_id=self.data.get("theme_id"))
        return json_response(data=ListQuestionSchema().dump({"questions": questions}))