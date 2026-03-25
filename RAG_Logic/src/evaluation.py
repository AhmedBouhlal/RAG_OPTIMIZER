def evaluate_retrieval(input_dict):

    retrievals = input_dict["retrievals"]
    ground_truths = input_dict["ground_truths"]

    evaluations = []

    for retrieval in retrievals:

        query = retrieval["query"]
        results = retrieval["results"]

        # Find corresponding ground-truth (handle both "query" and "question" fields)
        gt = next((g for g in ground_truths if g.get("query", g.get("question", "")) == query), None)
        if gt is None:
            continue

        # Ensure answers is a list
        answers = gt.get("answer", [])
        if not isinstance(answers, list):
            answers = [answers]

        # Enhanced scoring: 0.0 initially, then update based on keyword matches
        score = 0.0
        matched_count = 0
        total_keywords = len(answers)

        for r in results:
            r_text = r["text"].lower()
            for ans in answers:
                if ans.lower() in r_text:
                    matched_count += 1
                    # Don't break - check all results for best match
                    # break

        # Calculate score based on percentage of keywords matched
        if total_keywords > 0:
            match_percentage = matched_count / total_keywords
            if match_percentage >= 1.0:  # All keywords matched
                score = 5.0  # Très fidèle
            elif match_percentage >= 0.75:  # Most keywords matched
                score = 4.0  # Correct
            elif match_percentage >= 0.5:  # Half keywords matched
                score = 3.0  # Partiel
            elif match_percentage > 0:  # Some keywords matched
                score = 2.0  # Faible
            else:  # No keywords matched
                score = 1.0  # Incorrect

        eval_dict = {
            "query": query,
            "ground_truth": answers,
            "results": results,
            "retrieval_score": score,
        }

        evaluations.append(eval_dict)

    output = {
        "evaluations": evaluations
    }

    return output