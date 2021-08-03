import click
import os
import pandas as pd
import matplotlib.pyplot as plt
from audio_file import AudioFile

plt.close('all')

audio_ext = {'wav',}

def rm_non_audio(file_list):
    return [f for f in file_list if f.split('.')[-1] in audio_ext]


def dir_to_files(files):
    new_files = []
    for f in files:
        if os.path.isdir(f):
            new_files.extend([os.path.join(f, x) for x in os.listdir(f)])
        else:
            new_files.append(f)

    return sorted(rm_non_audio(new_files))


def run(files, short_target, integrated_target, do_plot):
    files = dir_to_files(files)

    file_objs = list(map(AudioFile, files))

    df = pd.DataFrame(columns=['Sample Rate', 'Length', 'LU-I', 'Max LU-S', 'Max LU-S Time', 'Min LU-S',
                               'Min LU-S Time', 'Peak L', 'Peak R', 'PLR', 'Min PSR'])

    if do_plot and len(file_objs) > 1:
        fig, axes = plt.subplots(nrows=len(file_objs) + 1, constrained_layout=True)
    else:
        axes = None

    for i, a in enumerate(file_objs):
        df.loc[a.file_path] = a.calc_row(short_target=short_target, plot=i if do_plot else None, axes=axes)

    if len(file_objs) > 1:
        total = sum(file_objs)
        df.loc['Total'] = total.calc_row(short_target=short_target, plot=len(file_objs) if do_plot else None, axes=axes)

    return df

@click.command()
@click.option('-f', '--files', multiple=True, type=click.Path(exists=True), help='File or folder to use.')
@click.option('-s', '--short-target', type=click.FLOAT, default=-9, help='Max for short-term loudness')
@click.option('-i', '--integrated-target', type=click.FLOAT, default=None, help='Max for integrated loudness')
@click.option('-p', '--do-plot', is_flag=True, help='Show plots')
def main(files, short_target, integrated_target, do_plot):
    df = run(files, short_target, integrated_target, do_plot)

    df = df.round(3)

    for target_col, target in (('LU-I', integrated_target), ('Max LU-S', short_target)):
        if target is not None:
            target_mask = df[target_col] > target
            df[target_col] = df[target_col].astype(str)
            df.loc[target_mask, target_col] = df.loc[target_mask, target_col].apply(click.style, fg='yellow')
            df.loc[~target_mask, target_col] = df.loc[~target_mask, target_col].apply(click.style, fg='white')
            df = df.rename(columns={target_col: click.style(target_col, fg='green')})

    with pd.option_context("display.max_rows", 100, "display.max_columns", 100, 'display.expand_frame_repr', False):
        str_df = str(df)

    print(str_df)

    plt.show()


if __name__ == '__main__':
    main()
