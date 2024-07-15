import json


def get_filepath(path, params):
    match params.id:
        case "1D" | "2D":
            if params.euclid_resample:
                return f"{path}/{params.id}+res_{params.radius}.json"
            else:
                return f"{path}/{params.id}_{params.radius}.json"
        case "Res":
            return f"{path}/{params.id}_{params.rho}_{params.phi}.json"
        case _:
            raise ValueError


def write_data(path, params, results):
    with open(get_filepath(path, params), "w") as fp:
        json.dump(results, fp)


def read_data(path, params):
    with open(get_filepath(path, params), 'rb') as fp:
        out = json.load(fp)

    return out
