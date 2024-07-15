from abcvoting import scores
from abcvoting.abcrules import Rule, UnknownAlgorithm, _seq_thiele_irresolute, ALGORITHM_NAMES, \
    MAX_NUM_OF_COMMITTEES_DEFAULT
from abcvoting.misc import sorted_committees
from abcvoting.misc import str_committees_with_header, header, str_set_of_candidates
from abcvoting.output import output, DETAILS


# Adapt abcvotings computation of seqThiele to also return order in which candidates were chosen

def compute_seq_thiele_method_return_order(
        scorefct_id,
        profile,
        committeesize,
        algorithm="fastest",
        resolute=True,
        max_num_of_committees=MAX_NUM_OF_COMMITTEES_DEFAULT,
):
    """
    Sequential Thiele methods.

    For a mathematical description of these rules, see e.g.
    "Multi-Winner Voting with Approval Preferences".
    Martin Lackner and Piotr Skowron.
    <http://dx.doi.org/10.1007/978-3-031-09016-5>

    Parameters
    ----------
        scorefct_id : str
            A string identifying the score function that defines the Thiele method.

        profile : abcvoting.preferences.Profile
            A profile.

        committeesize : int
            The desired committee size.

        algorithm : str, optional
            The algorithm to be used.

        resolute : bool, optional
            Return only one winning committee.

            If `resolute=False`, all winning committees are computed (subject to
            `max_num_of_committees`).

        max_num_of_committees : int, optional
             At most `max_num_of_committees` winning committees are computed.

             If `max_num_of_committees=None`, the number of winning committees is not restricted.
             The default value of `max_num_of_committees` can be modified via the constant
             `MAX_NUM_OF_COMMITTEES_DEFAULT`.

    Returns
    -------
        list of CandidateSet
            A list of winning committees.
    """
    scores.get_marginal_scorefct(scorefct_id, committeesize)  # check that `scorefct_id` is valid
    rule_id = "seq" + scorefct_id
    rule = Rule(rule_id)
    if algorithm == "fastest":
        algorithm = rule.fastest_available_algorithm()
    rule.verify_compute_parameters(
        profile=profile,
        committeesize=committeesize,
        algorithm=algorithm,
        resolute=resolute,
        max_num_of_committees=max_num_of_committees,
    )

    COMMITTEE = []

    if algorithm == "standard":
        if resolute:
            committees, detailed_info, COMMITTEE = _seq_thiele_resolute_return_order(scorefct_id, profile,
                                                                                     committeesize)
        else:
            committees, detailed_info = _seq_thiele_irresolute(
                scorefct_id, profile, committeesize, max_num_of_committees
            )
    else:
        raise UnknownAlgorithm(rule_id, algorithm)

    # optional output
    output.info(header(rule.longname), wrap=False)
    if not resolute:
        output.info("Computing all possible winning committees for any tiebreaking order")
        output.info(" (aka parallel universes tiebreaking) (resolute=False)\n")
    if output.verbosity <= DETAILS:  # skip thiele_score() calculations if not necessary
        output.details(f"Algorithm: {ALGORITHM_NAMES[algorithm]}\n")
        if resolute:
            output.details(
                f"starting with the empty committee (score = "
                f"{scores.thiele_score(scorefct_id, profile, [])})\n"
            )
            committee = []
            for i, next_cand in enumerate(detailed_info["next_cand"]):
                tied_cands = detailed_info["tied_cands"][i]
                delta_score = detailed_info["delta_score"][i]
                committee.append(next_cand)
                output.details(f"adding candidate number {i + 1}: {profile.cand_names[next_cand]}")
                output.details(
                    f"score increases by {delta_score} to"
                    f" a total of {scores.thiele_score(scorefct_id, profile, committee)}",
                    indent=" ",
                )
                if len(tied_cands) > 1:
                    output.details(f"tie broken in favor of {next_cand},\n", indent=" ")
                    output.details(
                        f"candidates "
                        f"{str_set_of_candidates(tied_cands, cand_names=profile.cand_names)} "
                        "are tied"
                    )
                    output.details(
                        f"(all would increase the score by the same amount {delta_score})",
                        indent=" ",
                    )
                output.details("")
    output.info(
        str_committees_with_header(committees, cand_names=profile.cand_names, winning=True)
    )

    if output.verbosity <= DETAILS:  # skip thiele_score() calculations if not necessary
        output.details(scorefct_id.upper() + "-score of winning committee(s):")
        for committee in committees:
            output.details(
                f"{str_set_of_candidates(committee, cand_names=profile.cand_names)}: "
                f"{scores.thiele_score(scorefct_id, profile, committee)}",
                indent=" ",
            )
        output.details("\n")
    # end of optional output

    if resolute:
        return sorted_committees(committees)[0], COMMITTEE
    else:
        return sorted_committees(committees)


def _seq_thiele_resolute_return_order(scorefct_id, profile, committeesize):
    """Compute one winning committee (=resolute) for sequential Thiele methods.

    Tiebreaking between candidates in favor of candidate with smaller
    number/index (candidates with larger numbers get deleted first).
    """
    committee = []
    marginal_scorefct = scores.get_marginal_scorefct(scorefct_id, committeesize)
    detailed_info = {"next_cand": [], "tied_cands": [], "delta_score": []}

    # build a committee starting with the empty set
    for _ in range(committeesize):
        additional_score_cand = scores.marginal_thiele_scores_add(
            marginal_scorefct, profile, committee
        )
        """
        tied_cands = [
            cand
            for cand in range(len(additional_score_cand))
            if additional_score_cand[cand] == max(additional_score_cand)
        ]
        next_cand = tied_cands[0]  # tiebreaking in favor of candidate with smallest index
        """
        # Do equivalent but more efficient version
        next_cand = max(enumerate(additional_score_cand), key=lambda x: x[1])[0]
        committee.append(next_cand)
        detailed_info["next_cand"].append(next_cand)
        # detailed_info["tied_cands"].append(tied_cands)
        detailed_info["delta_score"].append(max(additional_score_cand))

    return sorted_committees([committee]), detailed_info, committee
