import statistics
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from matplotlib.ticker import FuncFormatter

from parameters import *
from util import read_data


plt.rcParams["figure.figsize"] = [7.50, 3.50]
plt.rcParams["figure.autolayout"] = True

plt.rcParams['font.family'] = 'DeJavu Serif'
plt.rcParams['font.serif'] = ['Times New Roman']

plt.rcParams.update({'font.size': 12})


def flatten(xss):
  return [x for xs in xss for x in xs]


def get_plot_title(params, rule, avg_approvals):
  match params.id:
    case "1D" | "2D":
      if params.euclid_resample:
        return f"{params.id}+res, radius: {params.radius}, Avg. #approvals: {avg_approvals}, Rule: {rule}"
      else:
        return f"{params.id}, radius: {params.radius}, Avg. #approvals: {avg_approvals}, Rule: {rule}"
    case "Res":
      return f"{params.id}, rho: {params.rho}, phi: {params.phi}, Avg. #approvals: {avg_approvals}, Rule: {rule}"
    case _:
      raise ValueError("Invalid preference id")


def create_plots_EXP1(params, rule, filename):
  match rule:
    case "seqcc":
      plt.figure(figsize=(4,3))
    case "seqpav":
      plt.figure(figsize=(3.7, 3))
    case _:
      raise ValueError

  results_avg_add, results_avg_del, results_avg_mix = [], [], []
  results = read_data(jsons_directory_path, params)[rule]["EXP1"]
  avg_approvals = statistics.mean(results["Approval_Counts"])

  for percentage in percentage_changes:
    results_avg_add.append(statistics.mean(flatten(results["ADD"][str(percentage)])))
    results_avg_del.append(statistics.mean(flatten(results["DEL"][str(percentage)])))
    results_avg_mix.append(statistics.mean(flatten(results["MIX"][str(percentage)])))

  plt.ylim([-0.1, 7.1])
  plt.yticks(np.arange(0, 8, 1))
  for i in range(8):
    plt.axhline(y=i, color='lightgray', linestyle='--', linewidth=0.5)

  #plt.title(get_plot_title(params, rule, avg_approvals))

  plt.gca().xaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"{round(100*x)}%"))
  #plt.gca().xaxis.set_major_locator(MultipleLocator(0.01))

  plt.plot(percentage_changes, results_avg_add, label='ADD')
  plt.plot(percentage_changes, results_avg_del, label='REMOVE')
  plt.plot(percentage_changes, results_avg_mix, label='MIX')

  #plt.xticks(np.arange(0, 0.1, 11))
  plt.legend(loc='best')

  plt.xlabel("% of changes", fontsize=15)
  plt.rcParams['text.usetex'] = True

  if rule == "seqcc":
    plt.ylabel(r"avg. $\mathrm{dist}\left(S, S'\right)$", fontsize=15)

  plt.savefig(graphs_png_directory_path + filename + '.png')

  pp = PdfPages(graphs_pdf_directory_path + filename + '.pdf')
  plt.savefig(pp, format='pdf')

  pp.close()
  plt.close()

  plt.rcParams['text.usetex'] = False



def create_plots_EXP2(params, rule, filename):
  match rule:
    case "seqcc":
      plt.figure(figsize=(4, 3))
    case "seqpav":
      plt.figure(figsize=(3.7, 3))
    case _:
      raise ValueError

  dists_to_opt = []
  results = read_data(jsons_directory_path, params)[rule]["EXP2"]
  avg_approvals = statistics.mean(results["Approval_Counts"])

  # declutter by dropping 0 and only taking every third value
  #local_percentage_changes = [pqercentage for i, percentage in enumerate(percentage_changes) if i % 3 == 1]

  # Hardcode after all
  local_percentage_changes = [0.001, 0.013, 0.033, 0.062, 0.1]


  for percentage in local_percentage_changes:
    num_ties = list(map(lambda x: x[0], flatten(results["MIX"][str(percentage)])))
    dists = list(map(lambda x: x[1], flatten(results["MIX"][str(percentage)])))
    dists_to_opt.append(dists)

  #plt.ylim([-0.1, 10.1])

  plt.ylim([-0.1, 10.5])
  plt.yticks(np.arange(0, 11, 1))
  for i in range(11):
    plt.axhline(y=i, color='lightgray', linestyle='--', linewidth=0.5)

  #plt.title(get_plot_title(params, rule, avg_approvals))

  plt.boxplot(dists_to_opt, showmeans=True, meanline=True)
  plt.xticks(range(1, len(local_percentage_changes) + 1), map(lambda x: f"{round(x*100, 2)}%", local_percentage_changes), fontsize=12)

  #plt.plot([], [], '--', linewidth=1, color='green', label='mean')
  #plt.plot([], [], '-', linewidth=1, color='orange', label='median')
  #plt.legend(loc='best')

  plt.xlabel("% of changes", fontsize=16)
  plt.rcParams['text.usetex'] = True

  if rule == "seqcc":
    plt.ylabel(r"$\mathrm{dist}\left(S, S_{\mathrm{lexi}}'\right) - \mathrm{dist}\left(S, S_{\mathrm{opt}}'\right)$", fontsize=12)

  plt.savefig(graphs_png_directory_path + filename + '.png')

  pp = PdfPages(graphs_pdf_directory_path + filename + '.pdf')
  plt.savefig(pp, format='pdf')

  pp.close()
  plt.close()

  plt.rcParams['text.usetex'] = False


def create_plots_EXP3(params, rule, filename):
  match rule:
    case "seqcc":
      plt.figure(figsize=(4, 3))
    case "seqpav":
      plt.figure(figsize=(3.6, 3))
    case _:
      raise ValueError

  percentage = percentage_changes[7] # TODO: corresponds to 0.025

  results = read_data(jsons_directory_path, params)[rule]["EXP3"]
  avg_approvals = statistics.mean(results["Approval_Counts"])

  plt.ylim([-1, 101])
  plt.yticks(np.arange(0, 101, 25))
  for i in range(0, 101, 25):
    plt.axhline(y=i, color='lightgray', linestyle='--', linewidth=0.5)

  #plt.title(get_plot_title(params, rule, avg_approvals))

  exchange_percentages = [[100*x/NUM_ITERATIONS for x in sub] for sub in results["MIX"][str(percentage)]]

  plt.boxplot(list(zip(*exchange_percentages)), showmeans=True, meanline=True)


  match rule:
    case "seqcc":
      plt.xlabel(f"Original committee ordered by when \nthey were chosen by Greedy-CC", fontsize=11)
      plt.ylabel("% of committees were \nthey are replaced", fontsize=12)
    case "seqpav":
      plt.xlabel(f"Original committee ordered by when \nthey were chosen by Greedy-PAV", fontsize=11)
    case _:
      raise ValueError()

  plt.savefig(graphs_png_directory_path + filename + '.png')

  pp = PdfPages(graphs_pdf_directory_path + filename + '.pdf')
  plt.savefig(pp, format='pdf')

  pp.close()
  plt.close()


if __name__ == '__main__':

  for params in parameter_list:
    for rule in RULE_IDS:

      match params.id:
        case "1D" | "2D":
          if params.euclid_resample:
            filename = f"{rule}_{params.id}+res_{params.radius}"
          else:
            filename = f"{rule}_{params.id}_{params.radius}"
        case "Res":
          filename = f"{rule}_{params.id}_{params.rho}_{params.phi}"
        case _:
          raise ValueError

      create_plots_EXP1(params, rule, "EXP1_" + filename)
      create_plots_EXP2(params, rule, "EXP2_" + filename)
      create_plots_EXP3(params, rule, "EXP3_" + filename)
