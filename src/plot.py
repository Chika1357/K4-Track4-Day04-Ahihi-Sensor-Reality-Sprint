"""
plot.py - TV5: Vẽ 3 plot chính: timeline, sai số vs offset, quỹ đạo

Plot:
  1. Timeline: vị trí vật thể theo thời gian (trước/sau bù)
  2. Error vs Offset: biểu đồ sai số theo offset
  3. Trajectory: quỹ đạo 2D của vật thể phía trước xe
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os


def plot_error_vs_offset(results_csv: str, output_dir: str = './plots'):
    """Vẽ plot: Sai số (E_pre, E_post) vs Offset"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    df = pd.read_csv(results_csv)
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    fig.suptitle('Error vs Offset (all scenarios)', fontsize=14, fontweight='bold')
    
    scenarios = df['scenario'].unique()
    colors = {'Straight Line': 'blue', 'Acceleration': 'green', 'Turning': 'red'}
    
    distances = df['distance_m'].unique()
    
    for idx, distance in enumerate(sorted(distances)):
        ax = axes[idx]
        
        df_dist = df[df['distance_m'] == distance]
        
        for scenario in scenarios:
            df_scenario = df_dist[df_dist['scenario'] == scenario]
            df_scenario = df_scenario.sort_values('offset_ms')
            
            color = colors.get(scenario, 'black')
            
            # Vẽ E_pre
            ax.plot(df_scenario['offset_ms'], df_scenario['e_pre_mean'],
                   marker='o', linestyle='-', color=color, alpha=0.5, label=f'{scenario} (pre)')
            
            # Vẽ E_post
            ax.plot(df_scenario['offset_ms'], df_scenario['e_post_mean'],
                   marker='s', linestyle='-', color=color, alpha=1.0, label=f'{scenario} (post)')
        
        # Vẽ ngưỡng
        ax.axhline(y=0.5, color='red', linestyle='--', linewidth=1, alpha=0.7, label='Threshold (0.5m)')
        
        ax.set_xlabel('Offset (ms)')
        ax.set_ylabel('Mean Error (m)')
        ax.set_title(f'Object at {distance}m')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'error_vs_offset.png')
    plt.savefig(output_path, dpi=100)
    print(f"✓ Saved: {output_path}")
    plt.close()


def plot_comparison_pre_post(results_csv: str, output_dir: str = './plots'):
    """Vẽ plot: So sánh E_pre vs E_post"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    df = pd.read_csv(results_csv)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    scenarios = df['scenario'].unique()
    colors = {'Straight Line': 'blue', 'Acceleration': 'green', 'Turning': 'red'}
    
    x_pos = np.arange(len(df))
    width = 0.35
    
    # Chỉ vẽ top 20 experiments để không quá chật
    df_plot = df.head(20)
    x_pos = np.arange(len(df_plot))
    
    ax.bar(x_pos - width/2, df_plot['e_pre_mean'], width, label='E_pre (before compensation)',
           alpha=0.8, color='lightcoral')
    ax.bar(x_pos + width/2, df_plot['e_post_mean'], width, label='E_post (after compensation)',
           alpha=0.8, color='lightgreen')
    
    ax.axhline(y=0.5, color='red', linestyle='--', linewidth=2, alpha=0.7, label='Threshold')
    
    ax.set_xlabel('Experiment')
    ax.set_ylabel('Mean Error (m)')
    ax.set_title('Error Before vs After Compensation (first 20)')
    ax.set_xticks(x_pos)
    ax.set_xticklabels([f"{row['scenario'][:3]}-{int(row['offset_ms'])}" 
                         for _, row in df_plot.iterrows()], rotation=45, fontsize=8)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'comparison_pre_post.png')
    plt.savefig(output_path, dpi=100)
    print(f"✓ Saved: {output_path}")
    plt.close()


def plot_failure_heatmap(results_csv: str, output_dir: str = './plots'):
    """Vẽ heatmap: Failure cases"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    df = pd.read_csv(results_csv)
    
    # Pivot để tạo matrix
    df['is_failure_int'] = df['is_failure'].astype(int)
    
    scenarios = sorted(df['scenario'].unique())
    offsets = sorted(df['offset_ms'].unique())
    distances = sorted(df['distance_m'].unique())
    
    fig, axes = plt.subplots(1, len(distances), figsize=(12, 4))
    
    for idx, distance in enumerate(distances):
        ax = axes[idx]
        
        df_dist = df[df['distance_m'] == distance]
        
        # Tạo matrix (scenario vs offset)
        matrix = np.zeros((len(scenarios), len(offsets)))
        for i, scenario in enumerate(scenarios):
            for j, offset in enumerate(offsets):
                mask = (df_dist['scenario'] == scenario) & (df_dist['offset_ms'] == offset)
                if mask.any():
                    matrix[i, j] = df_dist[mask]['e_post_mean'].values[0]
        
        im = ax.imshow(matrix, cmap='RdYlGn_r', aspect='auto')
        
        ax.set_xticks(np.arange(len(offsets)))
        ax.set_yticks(np.arange(len(scenarios)))
        ax.set_xticklabels(offsets)
        ax.set_yticklabels([s[:3] for s in scenarios])
        ax.set_xlabel('Offset (ms)')
        ax.set_title(f'E_post @ {distance}m')
        
        # Thêm text
        for i in range(len(scenarios)):
            for j in range(len(offsets)):
                text = ax.text(j, i, f'{matrix[i, j]:.2f}',
                             ha="center", va="center", color="black", fontsize=8)
        
        plt.colorbar(im, ax=ax, label='Error (m)')
    
    fig.suptitle('E_post Heatmap by Scenario and Offset', fontsize=14, fontweight='bold')
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'failure_heatmap.png')
    plt.savefig(output_path, dpi=100)
    print(f"✓ Saved: {output_path}")
    plt.close()


if __name__ == "__main__":
    import sys
    
    results_csv = sys.argv[1] if len(sys.argv) > 1 else './results/results.csv'
    output_dir = sys.argv[2] if len(sys.argv) > 2 else './plots'
    
    if os.path.exists(results_csv):
        print(f"Generating plots from {results_csv}...\n")
        
        plot_error_vs_offset(results_csv, output_dir)
        plot_comparison_pre_post(results_csv, output_dir)
        plot_failure_heatmap(results_csv, output_dir)
        
        print(f"\n✓ All plots saved to {output_dir}/")
    else:
        print(f"Error: {results_csv} not found. Run benchmark first.")
        sys.exit(1)
