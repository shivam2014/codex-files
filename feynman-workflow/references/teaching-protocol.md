# Teaching Protocol — Examples & Anti-patterns

## Concrete Trace vs Generic Explanation

### Bad (generic, no execution path)
> "The system uses a vector database to store embeddings, which allows for semantic search queries."

### Good (traces one concrete input)
> User submits "How do I reset my password?" → `search.ts:12` calls `embedQuery(text)` → that POSTs to `/v1/embeddings` with `input: "How do I reset my password?"` → OpenAI returns `[0.023, -0.45, ..., 0.89]` (384 floats) → we cosine-similarity against all stored vectors in `vectors` table → top 5 chunks go to `buildPrompt()` → LLM generates answer.

### Bad (analogy for code)
> "Think of it like a filing cabinet where each drawer has a label."

### Good (describes the code)
> `handleSubmit()` reads `FormData.email` → calls `validateEmail()` which runs `/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)` → if false, sets `errors.email = "invalid format"` → returns early. If true, calls `POST /api/auth/login` with `{email, password}`.

---

## BEFORE→AFTER Diff

### Bad
> "I updated the validation function to handle empty strings."

### Good
```diff
 def validate_email(email):
-    if not email:
-        return False
-    return "@" in email
+    # BEFORE: return False for empty — didn't distinguish null from empty
+    # AFTER: returns None for empty (skip), False for invalid format
+    if not email:
+        return None  # skip, don't fail
+    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))
```

Diff must show:
- The **old and new** code
- **Why** the change was made (one sentence)
- The **execution-path effect** of the change

---

## One-Sentence Definitions

### Bad
> "A closure is a function that retains access to its lexical scope even when executed outside that scope. It's created when a function is defined inside another function and the inner function references variables from the outer function."

### Good
> "A closure is a function that carries its local variable bindings with it after the outer function returns."

---

## Interaction Rhythm Examples

### Orient (good)
> "We're fixing a 500 on `/checkout` when the cart is empty. The route handler `checkout.ts:23` calls `processPayment(cart.total)` which crashes because `cart.total` is `None` when cart is empty. Plan: trace the route → write a guard at `loadCart()` → add test."

### Execute (good)
> Opening `routes/checkout.ts:20-40`:
> ```diff
>  async function loadCart(userId: string): Cart {
>    const cart = await db.cart.findFirst({ where: { userId, status: "open" }});
> -  return cart;
> +  return cart ?? Cart.empty();
>  }
> ```
> **BEFORE:** `findFirst` returns `null` for no-cart users → `cart.total` throws `TypeError: Cannot read properties of null`.
> **AFTER:** `?? Cart.empty()` returns a Cart with `total: 0` → `processPayment(0)` returns early with `amount: 0`.

### Verify (good)
> `curl -X POST /checkout` returns `{"error": "empty_cart"}` instead of 500. Test added: `test/checkout.test.ts` asserts empty cart returns 422 with error body. Runs green.
