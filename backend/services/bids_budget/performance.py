def calculate_performance_score(conversions,
                                cost_per_conversion,
                                all_conversions,
                                cost_per_all_conversions,
                                clicks,
                                cost_micros,
                                impressions):
    
    performance_score = (conversions / cost_per_conversion) + \
                        (all_conversions / cost_per_all_conversions) + \
                        (clicks / cost_micros * 1_000_000) + \
                        (impressions / cost_micros * 1_000_000)
    
    print('metrics', conversions, cost_per_conversion, all_conversions, cost_per_all_conversions, clicks, cost_micros, impressions)
    print('performance_score', performance_score)
    return performance_score

def adjust_budget(initial_budget, performance_score):
    threshold = 1.1 # 10%
    benchmark = calculate_average_performance_score() * threshold
    
    if performance_score >= benchmark:
        return initial_budget * 1.20

    else:
        return initial_budget * 0.80

def calculate_average_performance_score():
    # TODO Implement this function
    return 1047
    
