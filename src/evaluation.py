def evaluate_retrieval(input_dict):

    retrievals = input_dict["retrievals"]
    ground_truths = input_dict["ground_truths"]

    evaluations = []

    for retrieval in retrievals:

        query = retrieval["query"]
        results = retrieval["results"]

        # Find corresponding ground-truth
        gt = next((g for g in ground_truths if g["query"] == query), None)

        if gt is None:
            continue

        answer = gt["answer"]

        # Simple scoring: 1 if any chunk contains answer, else 0
        score = 0.0
        for r in results:
            if answer.lower() in r["text"].lower():
                score = 1.0
                break

        eval_dict = {
            "query": query,
            "ground_truth": answer,
            "results": results,
            "retrieval_score": score
        }

        evaluations.append(eval_dict)

    output = {
        "evaluations": evaluations
    }

    return output
