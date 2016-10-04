
# 3p
from nose.tools import eq_, assert_raises
from requests import Session

# project
from ddtrace.contrib.requests import TracedSession
from ddtrace.ext import http, errors
from tests.test_tracer import get_test_tracer


class TestSession(object):

    @staticmethod
    def test_200():
        tracer, session = get_traced_session()
        out = session.get('http://httpstat.us/200')
        eq_(out.status_code, 200)
        # validation
        spans = tracer.writer.pop()
        eq_(len(spans), 1)
        s = spans[0]
        eq_(s.get_tag(http.METHOD), 'GET')
        eq_(s.get_tag(http.STATUS_CODE), '200')
        eq_(s.error, 0)

    @staticmethod
    def test_post_500():
        tracer, session = get_traced_session()
        out = session.post('http://httpstat.us/500')
        # validation
        eq_(out.status_code, 500)
        spans = tracer.writer.pop()
        eq_(len(spans), 1)
        s = spans[0]
        eq_(s.get_tag(http.METHOD), 'POST')
        eq_(s.get_tag(http.STATUS_CODE), '500')
        eq_(s.error, 1)

    @staticmethod
    def test_non_existant_url():
        tracer, session = get_traced_session()

        try:
            session.get('http://i.hope.this.will.never.ever.exist.purple.monkey.dishwasher')
        except Exception:
            pass
        else:
            assert 0, "expected error"

        spans = tracer.writer.pop()
        eq_(len(spans), 1)
        s = spans[0]
        eq_(s.get_tag(http.METHOD), 'GET')
        eq_(s.error, 1)
        assert "Name or service not known" in s.get_tag(errors.MSG)
        assert "Name or service not known" in s.get_tag(errors.STACK)
        assert "Traceback (most recent call last)" in s.get_tag(errors.STACK)
        assert "requests.exception" in s.get_tag(errors.TYPE)


    @staticmethod
    def test_500():
        tracer, session = get_traced_session()
        out = session.get('http://httpstat.us/500')
        eq_(out.status_code, 500)

        spans = tracer.writer.pop()
        eq_(len(spans), 1)
        s = spans[0]
        eq_(s.get_tag(http.METHOD), 'GET')
        eq_(s.get_tag(http.STATUS_CODE), '500')
        eq_(s.error, 1)


def get_traced_session():
    tracer = get_test_tracer()
    session = TracedSession()
    session.set_datadog_tracer(tracer)
    return tracer, session
