import sys
import bisect #binary search optimal
def solve_tennis_game():
    num_total_serves = int(sys.stdin.readline())
    serve_outcomes_str = sys.stdin.readline().split()
    serve_outcomes_list = [int(s) for s in serve_outcomes_str] #list of 1s and 2s

    #  stores the 0-based index of Petya's k-th win.
    petya_kth_win_indices = [-1]  #idx 0 can be unused so -1
    gena_kth_win_indices = [-1]

    for i in range(num_total_serves):
        if serve_outcomes_list[i] == 1: #petya won this serve
            petya_kth_win_indices.append(i)
        else: #gena
            gena_kth_win_indices.append(i)
    
    num_petya_wins_in_record = len(petya_kth_win_indices) - 1
    num_gena_wins_in_record = len(gena_kth_win_indices) - 1
    
    valid_s_t_results = []

    for points_to_win_a_set in range(1, num_total_serves + 1):
        petya_sets_won_simulation = 0
        gena_sets_won_simulation = 0        
        petya_serves_won_overall_sim = 0 
        gena_serves_won_overall_sim = 0   
        last_completed_set_serve_idx = -1 
        winner_of_last_simulated_set = 0 
        while True:
            petya_target_score_for_set = petya_serves_won_overall_sim + points_to_win_a_set
            idx_petya_wins_current_set = float('inf')
            if petya_target_score_for_set <= num_petya_wins_in_record:
                idx_petya_wins_current_set = petya_kth_win_indices[petya_target_score_for_set]
            gena_target_score_for_set = gena_serves_won_overall_sim + points_to_win_a_set
            idx_gena_wins_current_set = float('inf')
            if gena_target_score_for_set <= num_gena_wins_in_record:
                idx_gena_wins_current_set = gena_kth_win_indices[gena_target_score_for_set]
            if idx_petya_wins_current_set == float('inf') and idx_gena_wins_current_set == float('inf'):
                break 

            current_set_ends_at_idx = -1

            if idx_petya_wins_current_set < idx_gena_wins_current_set:
                petya_sets_won_simulation += 1
                winner_of_last_simulated_set = 1
                current_set_ends_at_idx = idx_petya_wins_current_set
                petya_serves_won_overall_sim = petya_target_score_for_set
                gena_serves_won_overall_sim = bisect.bisect_right(gena_kth_win_indices, current_set_ends_at_idx) -1            
            elif idx_gena_wins_current_set < idx_petya_wins_current_set:
                gena_sets_won_simulation += 1
                winner_of_last_simulated_set = 2
                current_set_ends_at_idx = idx_gena_wins_current_set
                
                gena_serves_won_overall_sim = gena_target_score_for_set
                petya_serves_won_overall_sim = bisect.bisect_right(petya_kth_win_indices, current_set_ends_at_idx) -1
            
            else: #both finish same serve idx
                current_set_ends_at_idx = idx_petya_wins_current_set
                if serve_outcomes_list[current_set_ends_at_idx] == 1: 
                    petya_sets_won_simulation += 1
                    winner_of_last_simulated_set = 1
                else: 
                    gena_sets_won_simulation += 1
                    winner_of_last_simulated_set = 2
            
                petya_serves_won_overall_sim = petya_target_score_for_set
                gena_serves_won_overall_sim = gena_target_score_for_set
            last_completed_set_serve_idx = current_set_ends_at_idx
            if last_completed_set_serve_idx == num_total_serves - 1:
                break

        if last_completed_set_serve_idx == num_total_serves - 1:
            actual_winner_of_last_record_serve = serve_outcomes_list[num_total_serves - 1]
            
            if winner_of_last_simulated_set == 1:  #petya won last simulated set
                if petya_sets_won_simulation > gena_sets_won_simulation: 
                    if actual_winner_of_last_record_serve == 1: 
                        valid_s_t_results.append( (petya_sets_won_simulation, points_to_win_a_set) )
            elif winner_of_last_simulated_set == 2: 
                if gena_sets_won_simulation > petya_sets_won_simulation: 
                    if actual_winner_of_last_record_serve == 2: # gena won record serve
                        valid_s_t_results.append( (gena_sets_won_simulation, points_to_win_a_set) )

    valid_s_t_results.sort() 
    sys.stdout.write(str(len(valid_s_t_results)) + "\n")
    for s_val, t_val in valid_s_t_results:
        sys.stdout.write(str(s_val) + " " + str(t_val) + "\n") # Print results

if __name__ == '__main__':
    solve_tennis_game()
