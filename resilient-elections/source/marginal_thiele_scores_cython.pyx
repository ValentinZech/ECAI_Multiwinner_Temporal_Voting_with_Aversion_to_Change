cimport cython

@cython.boundscheck(False)
@cython.wraparound(False)
def marginal_thiele_scores_add_cython(marginal_scorefct, profile, committee):
    cdef int num_cand = profile.num_cand
    cdef list marginal = [0] * num_cand
    cdef int intersectionsize
    cdef marginal_score  # can't be int, since fractions then get rounded to 0, i.e., pav == cc
    cdef int cand
    cdef double weight

    cdef list first_few_scores = [marginal_scorefct(i) for i in range(len(committee) + 2)]
    def precomputed_marginal_scorefct(i):
        if i < len(first_few_scores):
            return first_few_scores[i]
        else:
            raise RuntimeError  #return marginal_scorefct(i) <- don't need this, in case we precompute sufficiently many

    # Convert committee to a set for faster membership checks
    cdef set committee_set = set(committee)

    for voter in profile:
        intersectionsize = 0
        for cand in voter.approved:
            if cand in committee_set:
                intersectionsize += 1

        marginal_score = precomputed_marginal_scorefct(intersectionsize + 1)  # 25% of runtime in original program
        # => avoid recomputing for every candidate
        for cand in voter.approved:
            marginal[cand] += marginal_score

    for cand in committee:
        marginal[cand] = -1

    return marginal
