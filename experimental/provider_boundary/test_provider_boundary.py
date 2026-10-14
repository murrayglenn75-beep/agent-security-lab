import unittest

from provider_boundary import Provider, ProviderError, Request, Response, invoke

def req(**kwargs):return Request(**({"request_id":"r1","prompt":"hello","model":"test-model","max_tokens":50,"timeout_ms":1000,"max_cost_usd":0.5}|kwargs))
def good(r):return Response("ok","local","test-model",4,2,0.0)
def provider(name="local",fn=good,types=frozenset({"public"})):
 return Provider(name,fn,frozenset({"test-model"}),types,100)
POLICY={"allowed_providers":{"local","cloud"}}
class T(unittest.TestCase):
 def test_local(self):self.assertEqual(invoke(req(),[provider()],POLICY)[0].text,"ok")
 def test_reject_effects(self):
  with self.assertRaises(ValueError):invoke(req(effect_class="tool_call"),[provider()],POLICY)
 def test_denied_provider(self):
  with self.assertRaises(ProviderError):invoke(req(),[provider()],{"allowed_providers":set()})
 def test_privacy_denial(self):
  with self.assertRaises(ProviderError):invoke(req(data_class="confidential"),[provider()],POLICY)
 def test_invalid_budget(self):
  with self.assertRaises(ValueError):invoke(req(max_cost_usd=-1),[provider()],POLICY)
 def test_budget_ceiling(self):
  with self.assertRaises(ValueError):invoke(req(),[provider(fn=lambda r:Response("ok","local","test-model",1,2,9.0))],POLICY)
 def test_failure_without_fallback(self):
  def fail(r):raise ProviderError("TEMP",retryable=True)
  with self.assertRaises(ProviderError):invoke(req(),[provider(fn=fail),provider()],POLICY)
 def test_safe_fallback(self):
  def fail(r):raise ProviderError("TEMP",retryable=True)
  res,attempts=invoke(req(allow_fallback=True),[provider(fn=fail),provider()],POLICY)
  self.assertEqual(res.text,"ok");self.assertEqual(len(attempts),1)
 def test_no_fallback_for_terminal(self):
  def fail(r):raise ProviderError("PERMANENT",retryable=False)
  with self.assertRaises(ProviderError):invoke(req(allow_fallback=True),[provider(fn=fail),provider()],POLICY)
 def test_no_model_substitution(self):
  with self.assertRaises(ValueError):invoke(req(),[provider(fn=lambda r:Response("ok","local","other",0,0,0))],POLICY)
if __name__=="__main__":unittest.main()
