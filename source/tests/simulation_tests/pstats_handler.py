import pstats

if __name__ == "__main__":

    p = pstats.Stats('demote_only_stats')
    #p.sort_stats('cumulative').print_stats(30)
    #p.sort_stats('ncalls').print_stats(30)
    p.sort_stats('time').print_stats(30)