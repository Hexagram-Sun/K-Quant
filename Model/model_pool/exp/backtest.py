import qlib
import pandas as pd
from qlib.utils.time import Freq
from qlib.utils import flatten_dict
from qlib.backtest import backtest, executor
from qlib.contrib.evaluate import risk_analysis
from qlib.contrib.strategy import TopkDropoutStrategy
import argparse
import warnings

warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
csi300_industry_map = {'农林牧渔': ['SZ002311', 'SZ300498', 'SZ002714'],
                       '基础化工': ['SH601216', 'SH600426', 'SH600989', 'SZ002601', 'SH600352', 'SH600309', 'SZ002064', 'SZ000408', 'SZ000792', 'SH603260'],
                       '钢铁': ['SH600010', 'SH600019', 'SZ000708'],
                       '有色金属': ['SH600219', 'SH601600', 'SH601899', 'SH600362', 'SH600489', 'SH600547', 'SH600111', 'SH603993', 'SH603799', 'SZ002466', 'SZ002460'],
                       '电子': ['SH600460', 'SZ002049', 'SH688008', 'SZ300223', 'SH603986', 'SH603501', 'SZ300661', 'SZ300782', 'SH603160', 'SH600584', 'SZ002371', 'SH688012', 'SZ002916', 'SZ002938', 'SH600183', 'SZ300408', 'SZ000100', 'SZ000725', 'SH688036', 'SH600745', 'SZ002475', 'SZ002600', 'SZ002241', 'SZ300433', 'SH601138'],
                       '汽车': ['SH600660', 'SH600741', 'SZ000338', 'SH601966', 'SH601799', 'SZ002920', 'SZ002594', 'SH601238', 'SH600104', 'SZ000625', 'SH601633'],
                       '家用电器': ['SZ000651', 'SZ000333', 'SH600690', 'SZ002032', 'SH603486', 'SZ002050'],
                       '食品饮料': ['SZ000895', 'SH600809', 'SH603369', 'SH600519', 'SZ002304', 'SZ000568', 'SZ000596', 'SZ000858', 'SH600132', 'SH600600', 'SZ002568', 'SH600887', 'SH603288'],
                       '轻工制造': ['SH603833', 'SH603899'],
                       '医药生物': ['SZ002001', 'SH600276', 'SH600196', 'SZ000963', 'SH600332', 'SH600085', 'SZ000538', 'SH600436', 'SZ002007', 'SH600161', 'SZ002252', 'SZ300122', 'SZ300142', 'SZ300601', 'SZ000661', 'SZ300760', 'SZ300595', 'SZ300529', 'SZ300003', 'SH603882', 'SZ300347', 'SH603259', 'SZ002821', 'SZ300759', 'SH600763', 'SZ300015'],
                       '公用事业': ['SH600795', 'SH600900', 'SH600886', 'SH600025', 'SZ003816', 'SH601985'],
                       '交通运输': ['SZ002120', 'SZ002352', 'SH601006', 'SH600029', 'SH601111', 'SH601021', 'SH600115', 'SH600009', 'SH601919'],
                       '房地产': ['SH600383', 'SZ000002', 'SH600606', 'SH600048', 'SH601155', 'SZ000069', 'SZ001979'],
                       '商贸零售': ['SH600655', 'SH601888'],
                       '社会服务': ['SZ002607', 'SZ002841'],
                       '银行': ['SH601398', 'SH601288', 'SH601328', 'SH600000', 'SH600016', 'SH600036', 'SH601166', 'SH601818', 'SH600015', 'SH601998', 'SH601916', 'SZ000001', 'SH601169', 'SH601009', 'SH600919', 'SZ002142', 'SH601229', 'SH600926', 'SH601838'],
                       '非银金融': ['SZ300059', 'SH601788', 'SH601688', 'SH600030', 'SZ002736', 'SZ000166', 'SH601901', 'SH601878', 'SH601066', 'SH601236', 'SH600958', 'SH600999', 'SH601377', 'SH601881', 'SH601211', 'SZ000776', 'SH600837', 'SH601336', 'SH601601', 'SH601318', 'SH601319', 'SH601628', 'SH600061'],
                       '建筑材料': ['SZ000877', 'SZ000786', 'SZ002791', 'SZ002271'],
                       '建筑装饰': ['SH601669', 'SH601117'],
                       '电力设备': ['SH600438', 'SZ002129', 'SH601012', 'SZ002459', 'SZ300763', 'SZ300274', 'SH603806', 'SH601865', 'SZ300316', 'SH603185', 'SZ300751', 'SZ002202', 'SZ300014', 'SZ300750', 'SZ300207', 'SZ002074', 'SH603659', 'SZ002709', 'SZ002812', 'SH688005', 'SZ300450', 'SH600089', 'SH601877', 'SH600406'],
                       '机械设备': ['SH601766', 'SZ000157', 'SZ000425', 'SH601100', 'SZ300124', 'SZ002008'],
                       '国防军工': ['SH601698', 'SZ000768', 'SH600760', 'SH600893', 'SH600150', 'SH601989', 'SZ002179', 'SZ002414'],
                       '计算机': ['SZ002236', 'SZ002415', 'SZ000066', 'SH603019', 'SZ000977', 'SZ000938', 'SZ300496', 'SH600845', 'SH600570', 'SZ002410', 'SZ300033', 'SZ300454', 'SH688111', 'SZ002230', 'SH600588'],
                       '传媒': ['SZ002602', 'SZ002555', 'SZ002027', 'SZ300413'],
                       '通信': ['SH600050', 'SZ000063', 'SZ300628'],
                       '煤炭': ['SH601088', 'SH601898', 'SH600188', 'SH601225'],
                       '石油石化': ['SH601808', 'SZ000301', 'SZ000703', 'SZ002493', 'SH600028', 'SH600346', 'SZ002648'],
                       '美容护理': ['SH688363']
}

hot_industry = {'dianzi': '电子', 'yiyaoshengwu': '医药生物', 'yinhang': '银行', 'feiyinjinrong': '非银金融',
                       'dianlishebei': '电力设备', 'jisuanji': '计算机'}


def backtest_loop(args, data, model_name, EXECUTOR_CONFIG, backtest_config):
    data = data[[model_name]]
    data.columns = [['score']]

    FREQ = "day"
    STRATEGY_CONFIG = {
    "topk": int(args.topk),
    "n_drop": args.drop,
    "signal": data,
    }
    # strategy object
    strategy_obj = TopkDropoutStrategy(**STRATEGY_CONFIG)
    # executor object
    executor_obj = executor.SimulatorExecutor(**EXECUTOR_CONFIG)
    # backtest
    portfolio_metric_dict, indicator_dict = backtest(executor=executor_obj, strategy=strategy_obj, **backtest_config)
    analysis_freq = "{0}{1}".format(*Freq.parse(FREQ))
    # backtest info
    report_normal, positions_normal = portfolio_metric_dict.get(analysis_freq)
    # analysis
    analysis = dict()
    analysis["excess_return_without_cost"] = risk_analysis(
    report_normal["return"] - report_normal["bench"], freq=analysis_freq
    )

    analysis["excess_return_with_cost"] = risk_analysis(
    report_normal["return"] - report_normal["bench"] - report_normal["cost"], freq=analysis_freq
    )

    # analysis_df = pd.concat(analysis)
    # analysis_dict = flatten_dict(analysis_df["risk"].unstack().T.to_dict())
    benchmark_p = risk_analysis(report_normal["bench"], freq=analysis_freq)
    excess_return_wo_cost = analysis["excess_return_without_cost"]
    excess_return_w_cost = analysis["excess_return_with_cost"]

    draw_df = report_normal[['return', 'bench']]
    draw_df.cumsum().to_csv(args.prefix + f"_" + model_name + "_" + args.time_scope + ".csv")
    return benchmark_p, excess_return_wo_cost, excess_return_w_cost


def back_test_main(args):
    data = pd.read_pickle(args.predicted_file)
    qlib.init(provider_uri=args.qlib_source)
    data = data.dropna()
    slc = slice(pd.Timestamp(args.backtest_start_date), pd.Timestamp(args.backtest_end_date))
    if args.industry_category != 'all':
        try:
            stock_list = csi300_industry_map[hot_industry[args.industry_category]]
            data = data.loc[(slc, stock_list), :]
            data = data.sort_index(level=0)
        except:
            print("wrong category key, return all stocks")
            data = data[slc]

    else:
        data = data[slc]

    CSI300_BENCH = "SH000300"
    EXECUTOR_CONFIG = {
        "time_per_step": "day",
        "generate_portfolio_metrics": True,
    }
    FREQ = 'day'
    backtest_config = {
        "start_time": args.backtest_start_date,
        "end_time": args.backtest_end_date,
        "account": 100000000,
        "benchmark": CSI300_BENCH,  # "benchmark": NASDAQ_BENCH,
        "exchange_kwargs": {
            "freq": FREQ,
            "limit_threshold": 0.095,
            "deal_price": "close",
            "open_cost": 0.00005,
            "close_cost": 0.00015,
            "min_cost": 5,
        }, }
    model_pool_name = data.columns.tolist()
    model_pool = [char for char in model_pool_name if char != 'label']
    pd_pool = []
    for model in model_pool:
        symbol = model
        benchmark, er_wo_cost, er_w_cost = backtest_loop(args, data, symbol, EXECUTOR_CONFIG, backtest_config)
        er_w_cost.columns = [[model + '_with_cost']]
        # er_wo_cost.columns = [[model + '_without_cost']]
        benchmark.columns = [['benchmarks']]
        if len(pd_pool) == 0:
            # pd_pool.extend([benchmark, er_w_cost, er_wo_cost])
            pd_pool.extend([benchmark, er_w_cost])
        else:
            # pd_pool.extend([er_w_cost, er_wo_cost])
            pd_pool.extend([er_w_cost])
    df = pd.concat(pd_pool, axis=1)
    df = df.T
    df.to_pickle(args.backtest_file)

    return None


def parse_args():
    """
    deliver arguments from json file to program
    :param param_dict: a dict that contains model info
    :return: no return
    """
    parser = argparse.ArgumentParser()
    # data
    parser.add_argument('--backtest_start_date', default='2023-04-01')
    parser.add_argument('--backtest_end_date', default='2024-04-30')
    parser.add_argument('--device', default='cuda:1')
    parser.add_argument('--time_scope', default='12_0')
    parser.add_argument('--prefix', default='pred_output/platform_data/backtest_data')
    parser.add_argument('--predicted_file', default='pred_output/ensemble_preds_latest.pkl')
    parser.add_argument('--backtest_file', default='pred_output/platform_data/backtest_result_all_12_1.pkl')
    parser.add_argument('--qlib_source', default='../../../stock_model/qlib_data/cn_data')
    parser.add_argument('--topk', default=5)
    parser.add_argument('--drop', default=0)
    parser.add_argument('--industry_category', default='dianzi')

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    back_test_main(args)