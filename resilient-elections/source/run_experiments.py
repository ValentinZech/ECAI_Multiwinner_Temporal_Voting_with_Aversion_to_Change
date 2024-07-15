import multiprocessing as mp
import random
from datetime import datetime, timedelta

import abcvoting
from abcvoting import abcrules
from abcvoting.generate import *
from numpy.random import default_rng
from tqdm import tqdm

from parameters import *
from util import write_data


# Monkey patch inefficient abcvoting method for own cython version (about 5 to 6x speedup)
from marginal_thiele_scores_cython import marginal_thiele_scores_add_cython
abcvoting.scores.marginal_thiele_scores_add = marginal_thiele_scores_add_cython

# Monkey patch seqThiele methods from abcvoting to also return order in which candidates were chosen
from overwrite_abcvoting_seqthiele import compute_seq_thiele_method_return_order
abcvoting.abcrules.compute_seq_thiele_method = compute_seq_thiele_method_return_order


## HELPER FUNCTIONS ##
def compute_committee_resolute(rule, profile, return_order=False):
    if return_order:
        return abcrules.compute(rule, profile, committeesize=COMMITTEE_SIZE, resolute=True)
    else:
        return abcrules.compute(rule, profile, committeesize=COMMITTEE_SIZE, resolute=True)[0]


compute_committees_irrresolute = lambda rule, profile: abcrules.compute(rule, profile, committeesize=COMMITTEE_SIZE,
                                                                        resolute=False,
                                                                        max_num_of_committees=MAX_NUM_COMMITTEES)
committee_distance = lambda S1, S2: len(S1 - S2)


def build_results_dict(accum: bool = False):
    results = {}
    for rule in RULE_IDS:
        results[rule] = {"EXP1": {}, "EXP2": {}, "EXP3": {}}

        results[rule]["EXP1"]["Approval_Counts"] = []
        for op in ["ADD", "DEL", "MIX"]:
            results[rule]["EXP1"][op] = {}
            for percentage in percentage_changes:
                results[rule]["EXP1"][op][percentage] = []

        results[rule]["EXP2"]["MIX"] = {}
        results[rule]["EXP2"]["Approval_Counts"] = []
        for percentage in percentage_changes:
            results[rule]["EXP2"][op][percentage] = []

        results[rule]["EXP3"]["MIX"] = {}
        results[rule]["EXP3"]["Approval_Counts"] = []
        for percentage in percentage_changes:
            if accum:
                results[rule]["EXP3"][op][percentage] = []
            else:
                results[rule]["EXP3"][op][percentage] = [0] * COMMITTEE_SIZE

    return results


def extend_results(accum_results, new_results):
    for rule in RULE_IDS:
        accum_results[rule]["EXP1"]["Approval_Counts"].extend(new_results[rule]["EXP1"]["Approval_Counts"])
        for op in ["ADD", "DEL", "MIX"]:
            for percentage in percentage_changes:
                accum_results[rule]["EXP1"][op][percentage].append(new_results[rule]["EXP1"][op][percentage])

        accum_results[rule]["EXP2"]["Approval_Counts"].extend(new_results[rule]["EXP2"]["Approval_Counts"])
        for percentage in percentage_changes:
            accum_results[rule]["EXP2"]["MIX"][percentage].append(new_results[rule]["EXP2"][op][percentage])

        accum_results[rule]["EXP3"]["Approval_Counts"].extend(new_results[rule]["EXP3"]["Approval_Counts"])
        for percentage in percentage_changes:
            accum_results[rule]["EXP3"]["MIX"][percentage].append(new_results[rule]["EXP3"]["MIX"][percentage])


def sample_election(params):
    match params.id:
        case "1D" | "2D":
            distribution = PointProbabilityDistribution(params.dist_id)
            profile = random_euclidean_vcr_profile(NUM_VOTERS, NUM_CANDIDATES, distribution, distribution,
                                                   params.radius, 0)
            if params.euclid_resample:
                resample_euclidian_election(profile, params)
        case "Res":
            profile = random_resampling_profile(NUM_VOTERS, NUM_CANDIDATES, params.rho, params.phi)
        case _:
            raise ValueError

    return profile


def resample_euclidian_election(profile, params):
    rng = default_rng()
    for v in profile:
        v_rho = len(v.approved) / NUM_CANDIDATES
        for c in profile.candidates:
            if rng.random() < params.phi:
                if rng.random() < v_rho:
                    if c not in v.approved:
                        v.approved.add(c)
                elif c in v.approved:
                    v.approved.remove(c)


def run_one_election(params):
    profile = sample_election(params)

    results = build_results_dict()

    sample_space_add = [(v_idx, c) for v_idx, v in enumerate(profile) for c in (set(profile.candidates) - v.approved)]
    sample_space_del = [(v_idx, c) for v_idx, v in enumerate(profile) for c in v.approved]

    original_committees = {}
    for rule in RULE_IDS:
        original_committees[rule] = compute_committee_resolute(rule, profile, True)

        results[rule]["EXP1"]["Approval_Counts"].append(len(sample_space_del))
        results[rule]["EXP2"]["Approval_Counts"].append(len(sample_space_del))
        results[rule]["EXP3"]["Approval_Counts"].append(len(sample_space_del))

    for _ in range(NUM_ITERATIONS):
        highest_percentage = percentage_changes[-1]
        max_numeric_change = int(len(sample_space_del) * highest_percentage)

        to_add = random.sample(sample_space_add, k=max_numeric_change)
        to_del = random.sample(sample_space_del, k=max_numeric_change)

        mult_factor = 1 / highest_percentage
        split_indices = [int(mult_factor * percentage * max_numeric_change) for percentage in [0] + percentage_changes]

        to_add_split = [to_add[i:j] for i, j in zip(split_indices, split_indices[1:])]
        to_del_split = [to_del[i:j] for i, j in zip(split_indices, split_indices[1:])]
        to_mix_split = [(to_add_sub[:len(to_add_sub) // 2], to_del_sub[:len(to_del_sub) // 2]) for
                        to_add_sub, to_del_sub in zip(to_add_split, to_del_split)]

        # Collect data for ADD operation
        for percentage, sub_to_add in zip(percentage_changes, to_add_split):
            # Apply changes to profile
            for voter_idx, candidate_idx in sub_to_add:
                profile[voter_idx].approved.add(candidate_idx)

            # Collect data for EXP1
            for rule in RULE_IDS:
                committee_ori = original_committees[rule][0]
                committee_add = compute_committee_resolute(rule, profile)
                dist_add = committee_distance(committee_ori, committee_add)
                results[rule]["EXP1"]["ADD"][percentage].append(dist_add)

        # Revert profile to original state
        for sub_to_add in to_add_split:
            for voter_idx, candidate_idx in sub_to_add:
                profile[voter_idx].approved.remove(candidate_idx)

        # Collect data for REMOVE operation
        for percentage, sub_to_del in zip(percentage_changes, to_del_split):
            # Apply changes to profile
            for voter_idx, candidate_idx in sub_to_del:
                profile[voter_idx].approved.remove(candidate_idx)

            # Collect data for EXP1
            for rule in RULE_IDS:
                committee_ori = original_committees[rule][0]
                committee_del = compute_committee_resolute(rule, profile)
                dist_del = committee_distance(committee_ori, committee_del)
                results[rule]["EXP1"]["DEL"][percentage].append(dist_del)

        # Revert profile to original state
        for sub_to_del in to_del_split:
            for voter_idx, candidate_idx in sub_to_del:
                profile[voter_idx].approved.add(candidate_idx)

        # Collect data for MIX operation
        for percentage, (sub_to_add, sub_to_del) in zip(percentage_changes, to_mix_split):
            # Apply changes to profile
            for voter_idx, candidate_idx in sub_to_add:
                profile[voter_idx].approved.add(candidate_idx)
            for voter_idx, candidate_idx in sub_to_del:
                profile[voter_idx].approved.remove(candidate_idx)

            for rule in RULE_IDS:
                committee_ori, candidate_order = original_committees[rule]
                committee_mix = compute_committee_resolute(rule, profile)

                # Collect data for EXP1
                dist_mix = committee_distance(committee_ori, committee_mix)
                results[rule]["EXP1"]["MIX"][percentage].append(dist_mix)

                # Collect data for EXP2
                tied_committees_mix = compute_committees_irrresolute(rule, profile)
                dist_mix_min = min(
                    committee_distance(committee_ori, tied_committee) for tied_committee in tied_committees_mix)
                results[rule]["EXP2"]["MIX"][percentage].append((len(tied_committees_mix), dist_mix - dist_mix_min))

                # Collect data for EXP3
                for i, c in enumerate(candidate_order):
                    if c not in committee_mix:
                        results[rule]["EXP3"]["MIX"][percentage][i] += 1

        # Revert profile to original state
        for sub_to_add, sub_to_del in to_mix_split:
            for voter_idx, candidate_idx in sub_to_add:
                profile[voter_idx].approved.remove(candidate_idx)
            for voter_idx, candidate_idx in sub_to_del:
                profile[voter_idx].approved.add(candidate_idx)

    return results


if __name__ == '__main__':

    start_time = datetime.now()

    for i, params in enumerate(parameter_list):
        accum_results = build_results_dict(True)

        if MULTIPROCESSING:
            with mp.Pool(processes=mp.cpu_count()) as p:
                for new_results in tqdm(p.imap_unordered(run_one_election, [params] * NUM_ELECTIONS),
                                        total=NUM_ELECTIONS):
                    extend_results(accum_results, new_results)
        else:
            for _ in tqdm(range(NUM_ELECTIONS)):
                new_results = run_one_election(params)
                extend_results(accum_results, new_results)

        if WRITE_DATA:
            write_data(jsons_directory_path, params, accum_results)

        progress_percent = round(100 * (i + 1) / len(parameter_list), 2)
        print(f"{i + 1} out of {len(parameter_list)} parameter combinations done ({progress_percent}%).")
        time_taken = datetime.now() - start_time
        time_taken = timedelta(seconds=time_taken.seconds)
        estimate_remaining = (time_taken / (i + 1)) * (len(parameter_list) - (i + 1))
        estimate_remaining = timedelta(seconds=estimate_remaining.seconds)
        print(f"{time_taken} / ~{time_taken + estimate_remaining} (approx. {estimate_remaining} remaining).")
