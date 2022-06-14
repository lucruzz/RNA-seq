# RNA-seq Scientific Workflow
Workflow for RNA sequencing using the Parallel Scripting Library - Parsl.

# Running the workflow using SSD

**1. First step:** 
   ./run.sh
**2. Second step:**
   Set the JOBs variables with the ID of the jobs that are running.
**4. Third step:**
   sbatch --dependency=after:$JOB1,$JOB2,$JOB3,$JOB4,$JOB5,$JOB6 dep.sh
