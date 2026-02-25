import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams
from math import gcd
from functools import reduce


class TaskScheduler:
    def __init__(self, num_tasks, num_vms):
        self.num_tasks = num_tasks
        self.num_vms = num_vms
        self.task_requirements = [random.uniform(1000, 100000) for _ in range(num_tasks)]
        self.vm_capacities = [random.uniform(2000, 16000) for _ in range(num_vms)]
    
    def calculate_makespan(self, assignment):
        vm_loads = [0.0] * self.num_vms
        for task_idx, vm_idx in enumerate(assignment):
            execution_time = self.task_requirements[task_idx] / self.vm_capacities[vm_idx]
            vm_loads[vm_idx] += execution_time
        return max(vm_loads)
    
    def random_algorithm(self):
        assignment = [random.randint(0, self.num_vms - 1) for _ in range(self.num_tasks)]
        return self.calculate_makespan(assignment)
    
    def power_of_two_choices(self):
        vm_loads = [0.0] * self.num_vms
        assignment = []
        
        for task_idx in range(self.num_tasks):
            if self.num_vms < 2:
                chosen_vm = 0
                time_chosen = vm_loads[chosen_vm] + (self.task_requirements[task_idx] / self.vm_capacities[chosen_vm])
                vm_loads[chosen_vm] = time_chosen
                assignment.append(chosen_vm)
                continue

            vm1, vm2 = random.sample(range(self.num_vms), 2)
            
            time1 = vm_loads[vm1] + (self.task_requirements[task_idx] / self.vm_capacities[vm1])
            time2 = vm_loads[vm2] + (self.task_requirements[task_idx] / self.vm_capacities[vm2])
            
            if time1 <= time2:
                chosen_vm = vm1
                vm_loads[vm1] = time1
            else:
                chosen_vm = vm2
                vm_loads[vm2] = time2
            
            assignment.append(chosen_vm)
        
        return max(vm_loads)

    def weighted_round_robin(self): 
        task_indices = sorted(range(self.num_tasks), key=lambda i: self.task_requirements[i], reverse=True)
        
        max_cap = max(self.vm_capacities)
        min_cap = min(self.vm_capacities)
        weights = []
        for cap in self.vm_capacities:
            if max_cap > min_cap:
                normalized = int(((cap - min_cap) / (max_cap - min_cap)) * 99 + 1)
            else:
                normalized = 50
            weights.append(normalized)
        try:
            gcd_val = reduce(gcd, weights)
            if gcd_val > 1:
                weights = [w // gcd_val for w in weights]
        except:
            pass
        
        weights = [max(1, w) for w in weights]
        current_weights = [0] * self.num_vms
        effective_weights = weights.copy()
        vm_loads = [0.0] * self.num_vms
        vm_task_counts = [0] * self.num_vms  
        for task_idx in task_indices:
            for i in range(self.num_vms):
                current_weights[i] += effective_weights[i]
            best_vm = -1
            best_score = float('-inf')          
            for i in range(self.num_vms):
                potential_time = vm_loads[i] + (self.task_requirements[task_idx] / self.vm_capacities[i])
                if vm_loads[i] > 0:
                    normalized_load = (vm_loads[i] / self.vm_capacities[i]) * 100
                else:
                    normalized_load = 0               
                score = (current_weights[i] * 2.0) - normalized_load - (potential_time * 0.1)             
                if score > best_score:
                    best_score = score
                    best_vm = i
            execution_time = self.task_requirements[task_idx] / self.vm_capacities[best_vm]
            vm_loads[best_vm] += execution_time
            vm_task_counts[best_vm] += 1
            total_weight = sum(effective_weights)
            current_weights[best_vm] -= total_weight
            if self.num_tasks > 10: 
                avg_load = sum(vm_loads) / self.num_vms
                avg_tasks = sum(vm_task_counts) / self.num_vms
                if vm_loads[best_vm] > avg_load * 1.3 and vm_task_counts[best_vm] > avg_tasks * 1.2:
                    effective_weights[best_vm] = max(1, effective_weights[best_vm] - 1)
                elif vm_loads[best_vm] < avg_load * 0.7 and avg_load > 0:
                    effective_weights[best_vm] = min(weights[best_vm] * 2, effective_weights[best_vm] + 1)       
        return max(vm_loads)


def run_experiments(num_runs=20):
    results = []
    
    print("Scenario 1: Variable Tasks (50-250)")
    for num_tasks in range(50, 251, 50):        
        rnd_results = []
        po2c_results = []
        rrlb_results = []
        
        for run in range(num_runs):
            scheduler = TaskScheduler(num_tasks, 25)
            rnd_results.append(scheduler.random_algorithm())
            po2c_results.append(scheduler.power_of_two_choices())
            rrlb_results.append(scheduler.weighted_round_robin())
        
        results.append({
            'Scenario': 'Scenario 1',
            'Tasks': num_tasks,
            'VMs': 25,
            'RND_Avg': np.mean(rnd_results),
            'RND_Max': np.max(rnd_results),
            'RND_Min': np.min(rnd_results),
            'Po2C_Avg': np.mean(po2c_results),
            'Po2C_Max': np.max(po2c_results),
            'Po2C_Min': np.min(po2c_results),
            'RRLB_Avg': np.mean(rrlb_results),
            'RRLB_Max': np.max(rrlb_results),
            'RRLB_Min': np.min(rrlb_results)
        })
    
    print("Scenario 2: Fixed Tasks (200), Variable VMs (10-50)")
    for num_vms in range(10, 51, 10):        
        rnd_results = []
        po2c_results = []
        rrlb_results = []
        
        for run in range(num_runs):
            scheduler = TaskScheduler(200, num_vms)
            rnd_results.append(scheduler.random_algorithm())
            po2c_results.append(scheduler.power_of_two_choices())
            rrlb_results.append(scheduler.weighted_round_robin())
        
        results.append({
            'Scenario': 'Scenario 2',
            'Tasks': 200,
            'VMs': num_vms,
            'RND_Avg': np.mean(rnd_results),
            'RND_Max': np.max(rnd_results),
            'RND_Min': np.min(rnd_results),
            'Po2C_Avg': np.mean(po2c_results),
            'Po2C_Max': np.max(po2c_results),
            'Po2C_Min': np.min(po2c_results),
            'RRLB_Avg': np.mean(rrlb_results),
            'RRLB_Max': np.max(rrlb_results),
            'RRLB_Min': np.min(rrlb_results)
        })
    
    return pd.DataFrame(results)


def plot_results(df):
    scenario1 = df[df['Scenario'] == 'Scenario 1']
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # FIRST SCENARIO
    x = np.arange(len(scenario1))
    width = 0.25
    
    ax = axes[0]
    
    bars1 = ax.bar(x - width, scenario1['RND_Avg'], width, label='Random', color='#FF6B6B', alpha=0.8)
    bars2 = ax.bar(x, scenario1['Po2C_Avg'], width, label='Power of Two Choices', color='#4ECDC4', alpha=0.8)
    bars3 = ax.bar(x + width, scenario1['RRLB_Avg'], width, label='Weighted Round Robin', color='#95E1D3', alpha=0.8)
    
    for i, (idx, row) in enumerate(scenario1.iterrows()):
        ax.plot([i - width, i - width], [row['RND_Min'], row['RND_Max']], color='darkred', linewidth=2)
        ax.text(i - width, row['RND_Max'] + 5, f"{row['RND_Max']:.0f}", ha='center', va='bottom', fontsize=8, fontweight='bold')
        ax.text(i - width, row['RND_Min'] - 5, f"{row['RND_Min']:.0f}", ha='center', va='top', fontsize=8, fontweight='bold')
        ax.text(i - width, row['RND_Avg'], f"{row['RND_Avg']:.0f}", ha='center', va='center', fontsize=8, fontweight='bold', color='black')
        
        ax.plot([i, i], [row['Po2C_Min'], row['Po2C_Max']], color='darkgreen', linewidth=2)
        ax.text(i, row['Po2C_Max'] + 5, f"{row['Po2C_Max']:.0f}", ha='center', va='bottom', fontsize=8, fontweight='bold')
        ax.text(i, row['Po2C_Min'] - 5, f"{row['Po2C_Min']:.0f}", ha='center', va='top', fontsize=8, fontweight='bold')
        ax.text(i, row['Po2C_Avg'], f"{row['Po2C_Avg']:.0f}", ha='center', va='center', fontsize=8, fontweight='bold', color='black')
        
        ax.plot([i + width, i + width], [row['RRLB_Min'], row['RRLB_Max']], color='darkblue', linewidth=2)
        ax.text(i + width, row['RRLB_Max'] + 5, f"{row['RRLB_Max']:.0f}", ha='center', va='bottom', fontsize=8, fontweight='bold')
        ax.text(i + width, row['RRLB_Min'] - 5, f"{row['RRLB_Min']:.0f}", ha='center', va='top', fontsize=8, fontweight='bold')
        ax.text(i + width, row['RRLB_Avg'], f"{row['RRLB_Avg']:.0f}", ha='center', va='center', fontsize=8, fontweight='bold', color='black')
    
    ax.set_xlabel('Number of Tasks', fontsize=12, fontweight='bold')
    ax.set_ylabel('Makespan (seconds)', fontsize=12, fontweight='bold')
    ax.set_title('Scenario 1: Variable Tasks (VMs=25)', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(scenario1['Tasks'].values)
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # SECOND SCENARIO
    scenario2 = df[df['Scenario'] == 'Scenario 2']
    x2 = np.arange(len(scenario2))
    
    ax2 = axes[1]
    
    bars1_2 = ax2.bar(x2 - width, scenario2['RND_Avg'], width, label='Random', color='#FF6B6B', alpha=0.8)
    bars2_2 = ax2.bar(x2, scenario2['Po2C_Avg'], width, label='Power of Two Choices', color='#4ECDC4', alpha=0.8)
    bars3_2 = ax2.bar(x2 + width, scenario2['RRLB_Avg'], width, label='Weighted Round Robin', color='#95E1D3', alpha=0.8)
    
    for i, (idx, row) in enumerate(scenario2.iterrows()):
        ax2.plot([i - width, i - width], [row['RND_Min'], row['RND_Max']], color='darkred', linewidth=2)
        ax2.text(i - width, row['RND_Max'] + 10, f"{row['RND_Max']:.0f}", ha='center', va='bottom', fontsize=8, fontweight='bold')
        ax2.text(i - width, row['RND_Min'] - 10, f"{row['RND_Min']:.0f}", ha='center', va='top', fontsize=8, fontweight='bold')
        ax2.text(i - width, row['RND_Avg'], f"{row['RND_Avg']:.0f}", ha='center', va='center', fontsize=8, fontweight='bold', color='black')
        
        ax2.plot([i, i], [row['Po2C_Min'], row['Po2C_Max']], color='darkgreen', linewidth=2)
        ax2.text(i, row['Po2C_Max'] + 10, f"{row['Po2C_Max']:.0f}", ha='center', va='bottom', fontsize=8, fontweight='bold')
        ax2.text(i, row['Po2C_Min'] - 10, f"{row['Po2C_Min']:.0f}", ha='center', va='top', fontsize=8, fontweight='bold')
        ax2.text(i, row['Po2C_Avg'], f"{row['Po2C_Avg']:.0f}", ha='center', va='center', fontsize=8, fontweight='bold', color='black')
        
        ax2.plot([i + width, i + width], [row['RRLB_Min'], row['RRLB_Max']], color='darkblue', linewidth=2)
        ax2.text(i + width, row['RRLB_Max'] + 10, f"{row['RRLB_Max']:.0f}", ha='center', va='bottom', fontsize=8, fontweight='bold')
        ax2.text(i + width, row['RRLB_Min'] - 10, f"{row['RRLB_Min']:.0f}", ha='center', va='top', fontsize=8, fontweight='bold')
        ax2.text(i + width, row['RRLB_Avg'], f"{row['RRLB_Avg']:.0f}", ha='center', va='center', fontsize=8, fontweight='bold', color='black')
    
    ax2.set_xlabel('Number of VMs', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Makespan (seconds)', fontsize=12, fontweight='bold')
    ax2.set_title('Scenario 2: Variable VMs (Tasks=200)', fontsize=14, fontweight='bold')
    ax2.set_xticks(x2)
    ax2.set_xticklabels(scenario2['VMs'].values)
    ax2.legend(loc='upper right', fontsize=10)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig('task_scheduling_results.png', dpi=300, bbox_inches='tight')
    plt.show()


def main():
    print("=" * 60)
    results_df = run_experiments(num_runs=20)   
    results_df.to_excel('task_scheduling_results.xlsx', index=False)
    print("\n" + "=" * 60)
    print("Results saved to 'task_scheduling_results.xlsx'")
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    print(results_df.to_string(index=False))
    print("\n" + "=" * 60)
    plot_results(results_df)    

if __name__ == "__main__":
    main()