import base_model
import numpy as np
import multiprocessing


SAFE_CPU_CORES = max(1, multiprocessing.cpu_count()-2)


def run_simulation_wrapper(args):
    return base_model.main(*args)

def main():
    print(f"\nGrid Side Length: {base_model.GRID_SIZE}")
    print(f"Population Distribution (Empty, Red, Blue): {base_model.PROBABILITY_DISTRIBUTION}")
    
    start = float(input("Starting Threshold: "))
    end = float(input("Ending Threshold: "))
    precision = float(input("Precision: "))
    visualise = int(input("Visualise? (0/1): "))
    if not visualise:
        time_per_threshold = int(input("Number of times to compute per threshold (minimum 1): "))
        assert(time_per_threshold >= 1)

    if not visualise:
        cores_to_use = int(input("Cores to use (0 for max): "))
        if(cores_to_use == 0): cores_to_use = SAFE_CPU_CORES

   
    if(visualise == 1):  # If visualisng (Can't use multiprocessing)
        with open("schelling_stats.csv", 'w') as file:
            file.write("Threshold,Segregation_Percentage\n")

            for threshold in np.round(np.arange(start, end+precision, precision),2):
                segregation_percentage = base_model.main(threshold, 1)
                file.write(f"{threshold},{segregation_percentage}\n")
             
    else: # If not visualising (Using multiprocessing)
        assert(not visualise)
        with open("schelling_stats.csv", 'w') as file:
            file.write("Threshold,Segregation_Percentage\n" )

            print(f"Starting multiprocessing with {cores_to_use} cores...")
            with multiprocessing.Pool(processes=cores_to_use) as pool:
                for threshold in np.round(np.arange(start, end+precision, step=precision),2):
                    tasks = [(threshold, 0) for _ in range(time_per_threshold)]
                    
                    result = list(pool.imap_unordered(run_simulation_wrapper, tasks))

                    average = np.average(result)
                    file.write(f"{threshold},{average}\n")
                    print(f"{threshold} -> {average} done.")
                   


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()




# MAKE A FUNCTION TO STOP IN BASE_MODEL TO MAKE THE STOPPING AND SAVING LOGIC NICER
# STOP WHEN len(unhappy) == 0