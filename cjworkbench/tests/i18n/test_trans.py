from django.test import SimpleTestCase
from cjworkbench.i18n.trans import trans_html, trans, MessageTranslator
from cjworkbench.i18n import default_locale
from icu import ICUError


mock_message_id = (
    "some+crazy+id+that+will+never+be+actually+used+in+real+translation+files"
)


class TransTest(SimpleTestCase):
    # Tests that `parameters` argument replaces variables in the message.
    # 1) Parameters that do not exist in the message are ignored.
    # 2) Variables in the message for which no parameter has been given are ignored.
    def test_trans_params(self):
        self.assertEqual(
            trans(
                mock_message_id,
                default="Hello {a} {param_b} {c}!",
                parameters={"param_b": "there", "a": "you", "d": "tester"},
            ),
            "Hello you there {c}!",
        )

    # Tests that a programmer will break the system by including an invalid parameter
    def test_programmer_invalid_parameter_syntax(self):
        with self.assertRaises(ICUError):
            trans(
                mock_message_id,
                default="Hello {a b}",
                parameters={"a": "you", "b": "2"},
            )

    # Tests that a translator can't break our system by including an invalid parameter
    def test_translator_invalid_parameter_syntax(self):
        self.assertEqual(
            MessageTranslator(default_locale)._process_simple_message(
                "Hello {a b}", "Hello {a} {b}", parameters={"a": "you", "b": "!"}
            ),
            "Hello you !",
        )

    # Tests that a programmer can include a numeric variable in the message
    def test_programmer_numeric_parameter(self):
        self.assertEqual(
            trans(
                mock_message_id,
                default="Hello {a} {0} {b}",
                parameters={"a": "you", "0": "!", "b": "2"},
            ),
            "Hello you ! 2",
        )

    # Tests that a translator can use a numeric variable in the message
    def test_translator_numeric_parameter(self):
        self.assertEqual(
            MessageTranslator(default_locale)._process_simple_message(
                "Hey {a} {0} {b}",
                "Hello {a} {0} {b}",
                parameters={"a": "you", "b": "!", "0": "there"},
            ),
            "Hey you there !",
        )

    # Tests that a translator can't break our system by adding or removing variables in the message
    def test_translator_different_parameters(self):
        self.assertEqual(
            MessageTranslator(default_locale)._process_simple_message(
                "Hey {a} {c}", "Hello {a} {b}", parameters={"a": "you", "b": "!"}
            ),
            "Hey you {c}",
        )

    # Tests that HTML is not escaped
    def test_no_html_escape(self):
        self.assertEqual(
            trans(
                mock_message_id,
                default='Hello <a href="/you?a=n&b=e">you > {param_b}</a> my & friend',
                parameters={"param_b": "> there"},
            ),
            'Hello <a href="/you?a=n&b=e">you > > there</a> my & friend',
        )

    # Tests that plurals, selects and nested messages are fully supported
    def test_icu_support(self):
        message = (
            "Hello {a}, you have {g, select,"
            "   male {{n, plural,"
            "       =0 {no boys} one {# boy} other {# boys}"
            "   }}"
            "   female {{n, plural,"
            "       =0 {no girls} one {# girl} other {# girls}"
            "   }}"
            "   other {{n, plural,"
            "       =0 {no children} one {# child} other {# children}"
            "   }}"
            "}"
        )
        self.assertEqual(
            trans(
                mock_message_id,
                default=message,
                parameters={"a": "there", "g": "male", "n": 17},
            ),
            "Hello there, you have 17 boys",
        )
        self.assertEqual(
            trans(
                mock_message_id,
                default=message,
                parameters={"a": "there", "g": "female", "n": 18},
            ),
            "Hello there, you have 18 girls",
        )
        self.assertEqual(
            trans(
                mock_message_id,
                default=message,
                parameters={"a": "there", "g": "other", "n": 0},
            ),
            "Hello there, you have no children",
        )


class TransHtmlTest(SimpleTestCase):
    # Tests that `parameters` argument replaces variables in the message.
    # 1) Parameters that do not exist in the message are ignored.
    # 2) Variables in the message for which no parameter has been given are ignored.
    def test_trans_params(self):
        self.assertEqual(
            trans_html(
                default_locale,
                mock_message_id,
                default="Hello {a} {param_b} {c}!",
                parameters={"param_b": "there", "a": "you", "d": "tester"},
            ),
            "Hello you there {c}!",
        )

    # Tests that a programmer can include a numeric variable in the message
    def test_programmer_numeric_parameter_html(self):
        self.assertEqual(
            trans_html(
                default_locale,
                mock_message_id,
                default="Hello {a} {0} {b}",
                parameters={"a": "you", "0": "!", "b": "2"},
            ),
            "Hello you ! 2",
        )

    # Tests that a translator can use a numeric variable in the message
    def test_translator_numeric_parameter_html(self):
        self.assertEqual(
            MessageTranslator(default_locale)._process_html_message(
                "Hey {a} {0} {b}",
                "Hello {a} {0} {b}",
                parameters={"a": "you", "b": "!", "0": "there"},
            ),
            "Hey you there !",
        )

    # Tests that a translator can't break our system by adding or removing variables in the message
    def test_translator_different_parameters_html(self):
        self.assertEqual(
            MessageTranslator(default_locale)._process_html_message(
                "Hey {a} {c}", "Hello {a} {b}", parameters={"a": "you", "b": "!"}
            ),
            "Hey you {c}",
        )

    # Tests that tags in messages are replaced correctly.
    # 1) Tags in `tags` that are not in the message are ignored.
    # 2) Tags in the message but not in `tags` are ignored. At this point, their contents are kept, but this may change in the future.
    # 3) All attributes given for a tag in `tags` are used.
    # 4) Tag attributes existing in the message are ignored.
    def test_trans_tags(self):
        self.assertEqual(
            trans_html(
                default_locale,
                mock_message_id,
                default='<a0 id="nope">Hello</a0><b0>you</b0><div>there</div>',
                parameters={"a": "you"},
                tags={
                    "a0": {
                        "tag": "a",
                        "attrs": {
                            "href": "/you",
                            "class": "the test",
                            "data-target": "someid",
                        },
                    },
                    "span0": {"tag": "span", "attrs": {"id": "ignore"}},
                },
            ),
            '<a class="the test" data-target="someid" href="/you">Hello</a>youthere',
        )

    # Tests that nested tags in messages are not tolerated.
    # At this point, nested tags are ignored, but their contents are kept. This may change in the future.
    def test_trans_nested_tags(self):
        self.assertEqual(
            trans_html(
                default_locale,
                mock_message_id,
                default="<a0>Hello<b0>you</b0><div>there</div></a0>",
                parameters={"a": "you"},
                tags={
                    "a0": {"tag": "a", "attrs": {"href": "/you"}},
                    "b0": {"tag": "b", "attrs": {"id": "hi"}},
                },
            ),
            '<a href="/you">Helloyouthere</a>',
        )

    # Tests that parameters are substituted within tags
    def test_trans_params_in_tags(self):
        self.assertEqual(
            trans_html(
                default_locale,
                mock_message_id,
                default="<a0>Hello {name}</a0>{test}",
                parameters={"name": "you", "test": "!"},
                tags={"a0": {"tag": "a", "attrs": {"href": "/you"}}},
            ),
            '<a href="/you">Hello you</a>!',
        )

    # Tests that special characters in the text are escaped, in any depth
    def test_trans_escapes_text(self):
        self.assertEqual(
            trans_html(
                default_locale,
                mock_message_id,
                default="<a0>Hello &<b>&</b></a0>>",
                tags={"a0": {"tag": "a", "attrs": {"href": "/you"}}},
            ),
            '<a href="/you">Hello &amp;&amp;</a>&gt;',
        )

    # Tests that message parameters are escaped
    def test_trans_escapes_params(self):
        self.assertEqual(
            trans_html(
                default_locale,
                mock_message_id,
                default="<a0>Hello {name}</a0>{test}",
                parameters={"name": "<b>you</b>", "test": "<b>there</b>"},
                tags={"a0": {"tag": "a", "attrs": {"href": "/you"}}},
            ),
            '<a href="/you">Hello &lt;b&gt;you&lt;/b&gt;</a>&lt;b&gt;there&lt;/b&gt;',
        )

    # Tests that tag attributes in messages are escaped
    def test_trans_escapes_tag_attrs(self):
        self.assertEqual(
            trans_html(
                default_locale,
                mock_message_id,
                default="<a0>Hello</a0>",
                tags={"a0": {"tag": "a", "attrs": {"href": "/you?a=b&c=d"}}},
            ),
            '<a href="/you?a=b&amp;c=d">Hello</a>',
        )

    # Tests the combination of properties of placeholder tags and of message parameters.
    # 0) In settings where there are multiple tags, some of which have to be deleted, all of them are processed
    # 1) the `tags` argument is used to replace placeholders and they are escaped correctly
    # 2) Tags or tag placeholders that have no counterpart in the arguments are removed
    # 3) Special characters, except for the ones of valid tags, are escaped
    # 4) Nested tags are not tolerated
    # 5) `arg_XX` arguments are replaced and escaped correctly
    # 6) The same tag can appear multiple times
    def test_trans_tag_placeholders(self):
        self.assertEqual(
            trans_html(
                default_locale,
                mock_message_id,
                default='<span0 class="nope">Hello {first}</span0><span1></span1> <span0>{second}</span0> <a0>{a}<b></b></a0> < <a1>there<</a1>!<br /><script type="text/javascript" src="mybadscript.js"></script>',
                parameters={"a": "you", "first": "hello", "second": "&"},
                tags={
                    "a0": {"tag": "a", "attrs": {"href": "/you"}},
                    "a1": {
                        "tag": "a",
                        "attrs": {"href": "/there?a=b&c=d", "class": "red big"},
                    },
                    "span0": {"tag": "span", "attrs": {"id": "hi"}},
                },
            ),
            '<span id="hi">Hello hello</span> <span id="hi">&amp;</span> <a href="/you">you</a> &lt; <a class="red big" href="/there?a=b&amp;c=d">there&lt;</a>!',
        )

    # Tests that plurals, selects and nested messages are fully supported
    def test_icu_support(self):
        message = (
            "Hello {a}, you have {g, select,"
            "   male {{n, plural,"
            "       =0 {<em0>no</em0> boys} one {# boy} other {# boys}"
            "   }}"
            "   female {{n, plural,"
            "       =0 {<em0>no</em0> girls} one {# girl} other {# girls}"
            "   }}"
            "   other {{n, plural,"
            "       =0 {<em0>no</em0> children} one {# child} other {# children}"
            "   }}"
            "}"
        )
        self.assertEqual(
            trans_html(
                default_locale,
                mock_message_id,
                default=message,
                parameters={"a": "there", "g": "male", "n": 17},
                tags={"em0": {"tag": "em", "attrs": {}}},
            ),
            "Hello there, you have 17 boys",
        )
        self.assertEqual(
            trans_html(
                default_locale,
                mock_message_id,
                default=message,
                parameters={"a": "there", "g": "female", "n": 18},
                tags={"em0": {"tag": "em", "attrs": {}}},
            ),
            "Hello there, you have 18 girls",
        )
        self.assertEqual(
            trans_html(
                default_locale,
                mock_message_id,
                default=message,
                parameters={"a": "there", "g": "other", "n": 0},
                tags={"em0": {"tag": "em", "attrs": {}}},
            ),
            "Hello there, you have <em>no</em> children",
        )
