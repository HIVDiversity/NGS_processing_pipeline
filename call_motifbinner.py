#!/usr/bin/python3
from __future__ import print_function
from __future__ import division
import argparse
import subprocess
import regex


__author__ = 'Colin Anthony'


def get_primer_lens_score(primer, pid_primer):

    primer = primer.upper()
    pid = False

    if primer.startswith("N"):
        pid = True
        pattern = r"(^[N]+)([ACGTRYMKSWHBVD]+[N]*[ACGTRYMKSWHBVDN]+[ACGT]$)"
    else:
        pattern = r"([^ACGT][ACGTRYMKSWHBVD]+[N]*[ACGTRYMKSWHBVDN]+[ACGT]$)"

    match = regex.match(pattern, primer.upper())
    if not match:
        print("invalid primer sequence", primer)
        raise TypeError

    if pid:
        pid_str = match.group(1)
        primer_seq = match.group(2)
    else:
        pid_str = ''
        primer_seq = match.group(1)

    len_pid = len(pid_str)
    len_primer_seq  = len(primer_seq)
    total_len = len(primer)
    if len_pid + len_primer_seq != total_len:
        print("invalid primer sequence, pid legnth and primer seq length don't add up to total length", primer)
        raise ValueError

    if pid and pid_primer and len_pid <= 7:
        print("PID length too short")
        raise ValueError

    if len_primer_seq < 10:
        print("Primer length too short")
        raise ValueError

    if len_pid > 14:
        primer_lens = '4,' + str(len_pid - 4) + "," + str(len_primer_seq)
    else:
        primer_lens = '1,' + str(len_pid - 1) + "," + str(len_primer_seq)

    primer_score = str(len_pid + int((len_primer_seq * 0.8)))

    return primer_lens, primer_score


def run_motifbinner(logfile, fwd_read, rev_read, outpath, fwd_primer, fwd_primer_lens, fwd_primer_score,
                    cDNA_primer, cDNA_primer_lens, cDNA_primer_score, name_prefix, counter, cores, nonoverlap):
    if not nonoverlap:
        overlap_option = "overlapping"
    else:
        overlap_option = "non_overlapping"

    fwd_pid = 'NULL'
    rev_pid_fragment = 2
    cmd = 'MotifBinner2.R --fwd_file={0} ' \
          '--fwd_primer_seq={1} ' \
          '--fwd_primer_lens={2} ' \
          '--fwd_primer_min_score={3} ' \
          '--rev_file={4} ' \
          '--rev_primer_seq={5} ' \
          '--rev_primer_lens={6} ' \
          '--rev_primer_min_score={7} ' \
          '--fwd_pid_in_which_fragment={8} ' \
          '--rev_pid_in_which_fragment={9} ' \
          '--output_dir={10} ' \
          '--base_for_names={11} ' \
          '--ncpu={12} ' \
          '--min_read_length=290 '\
          '--merged_read_length=240 '\
          '--{13}'.format(fwd_read,
                          fwd_primer,
                          fwd_primer_lens,
                          fwd_primer_score,
                          rev_read,
                          cDNA_primer,
                          cDNA_primer_lens,
                          cDNA_primer_score,
                          fwd_pid,
                          rev_pid_fragment,
                          outpath,
                          name_prefix,
                          cores,
                          overlap_option)

    # only write to log file if this is the first iteration
    if counter == 0:
        with open(logfile, 'a') as handle:
            handle.write("MotifBinner2 commands:\n{0}\n".format(cmd))
    print(cmd)
    subprocess.call(cmd, shell=True)


def main(read1, read2, outpath, fwd_primer, cDNA_primer, name_prefix, counter, logfile, cores, non_overlap ):

    print("calling MotifBinner")
    fwd_primer = fwd_primer.upper()
    cDNA_primer = cDNA_primer.upper()

    # calculate the primer lengths
    pid_primer = False
    fwd_primer_lens, fwd_primer_score = get_primer_lens_score(fwd_primer, pid_primer)
    pid_primer = True
    cDNA_primer_lens, cDNA_primer_score = get_primer_lens_score(cDNA_primer, pid_primer)

    # run motifbinner call function
    run_motifbinner(logfile, read1, read2, outpath, fwd_primer, fwd_primer_lens, fwd_primer_score,
                    cDNA_primer, cDNA_primer_lens, cDNA_primer_score, name_prefix, counter, cores, non_overlap)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calls the MotifBinner.R script to bin sequences by primer ID',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-r1', '--read1', default=argparse.SUPPRESS, type=str,
                        help='The read1 (R1) fastq file', required=True)
    parser.add_argument('-r2', '--read2', default=argparse.SUPPRESS, type=str,
                        help='The read2 (R2) fastq file', required=True)
    parser.add_argument('-o', '--outpath', default=argparse.SUPPRESS, type=str,
                        help='The path to where the output file will be created', required=True)
    parser.add_argument('-f', '--fwd_primer', default=argparse.SUPPRESS, type=str,
                        help='The fwd primer for these samples', required=True)
    parser.add_argument('-r', '--cDNA_primer', default=argparse.SUPPRESS, type=str,
                        help='The cDNA primer for these samples', required=True)
    parser.add_argument('-n', '--name_prefix', default=argparse.SUPPRESS, type=str,
                        help='The prefix for labeling sequence headers', required=True)
    parser.add_argument('-c', '--counter', default=argparse.SUPPRESS, type=str,
                        help='Counter to keep track of logging commands to the log file', required=True)
    parser.add_argument('-l', '--logfile', default=argparse.SUPPRESS, type=str,
                        help='The path and name of the log file', required=True)
    parser.add_argument('-ncpu', '--cores', default=3, type=int,
                        help='the number of CPU cores to use', required=False)
    parser.add_argument('-v', '--non_overlap', default=False, action='store_true',
                        help="Use if reads don't overlap)", required=False)

    args = parser.parse_args()
    read1 = args.read1
    read2 = args.read2
    outpath = args.outpath
    fwd_primer = args.fwd_primer
    cDNA_primer = args.cDNA_primer
    name_prefix = args.name_prefix
    counter = args.counter
    non_overlap = args.non_overlap
    cores = args.cores
    logfile = args.logfile

    main(read1, read2, outpath, fwd_primer, cDNA_primer, name_prefix, counter, logfile, cores, non_overlap)
