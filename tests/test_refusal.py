import unittest
from src.refusal import RefusalResponse, build_refusal_response


class TestRefusalSystem(unittest.TestCase):

    def test_refusal_response_formatting(self):
        refusal = RefusalResponse(
            question="Can my friend submit an appeal for me?",
            reason="The policy manual discusses appeal timelines but does not state whether a friend may submit on behalf of an applicant.",
            next_step="Refer the case to the Benefits Policy Supervisor.",
            status="REFUSED",
        )
        formatted = refusal.format_cli()

        self.assertIn("GROUNDED POLICY ASSISTANT", formatted)
        self.assertIn("Question:\n> Can my friend submit an appeal for me?", formatted)
        self.assertIn("REFUSAL", formatted)
        self.assertIn("The manual does not settle this question with sufficient confidence.", formatted)
        self.assertIn("Reason:\nThe policy manual discusses appeal timelines", formatted)
        self.assertIn("Next step:\nRefer the case to the Benefits Policy Supervisor.", formatted)
        self.assertIn("STATUS: REFUSED", formatted)

    def test_build_refusal_response_helper(self):
        refusal = build_refusal_response(
            question="What is the capital city of Australia?",
            reason="No policy evidence was retrieved for the question.",
        )
        self.assertEqual(refusal.status, "REFUSED")
        self.assertIn("Benefits Policy Supervisor", refusal.next_step)
        self.assertIn("No policy evidence", refusal.reason)


if __name__ == "__main__":
    unittest.main()
