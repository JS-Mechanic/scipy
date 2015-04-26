"""
A script that uses f2py to generate the signature files used to make
the Cython BLAS and LAPACK wrappers from the fortran source code for
LAPACK and the reference BLAS.

To generate the BLAS wrapper signatures call:
python _cython_signature_generator.py blas <blas_directory> <out_file>

To generate the LAPACK wrapper signatures call:
python _cython_signature_generator.py lapack <lapack_src_directory> <out_file>
"""

import glob
from numpy.f2py import crackfortran

sig_types = {'integer':'int',
             'complex':'c',
             'double precision':'d',
             'real':'s',
             'complex*16':'z',
             'double complex':'z',
             'character':'char',
             'logical':'bint'}

def get_type(info, arg):
    argtype = sig_types[info['vars'][arg]['typespec']]
    if argtype == 'c' and info['vars'][arg].get('kindselector') is not None:
        argtype = 'z'
    return argtype

def make_signature(filename):
    info = crackfortran.crackfortran(filename)[0]
    name = info['name']
    if info['block'] == 'subroutine':
        return_type = 'void'
    else:
        return_type = get_type(info, name)
    arglist = [' *'.join([get_type(info, arg), arg]) for arg in info['args']]
    args = ', '.join(arglist)
    # Eliminate strange variable naming that replaces rank with rank_bn.
    args = args.replace('rank_bn', 'rank')
    return '{} {}({})\n'.format(return_type, name, args)

def get_sig_name(line):
    return line.split('(')[0].split(' ')[-1]

def sigs_from_dir(directory, outfile, manual_wrappers=None, exclusions=None):
    if directory[-1] in ['/', '\\']:
        directory = directory[:-1]
    files = glob.glob(directory + '/*.f*')
    if exclusions is None:
        exclusions = []
    if manual_wrappers is not None:
        exclusions += [get_sig_name(l) for l in manual_wrappers.split('\n')]
    signatures = []
    for filename in files:
        name = filename.split('\\')[-1][:-2]
        if name in exclusions:
            continue
        signatures.append(make_signature(filename))
    if manual_wrappers is not None:
        signatures += [l + '\n' for l in manual_wrappers.split('\n')]
    signatures.sort(key=get_sig_name)
    comment = ["# This file was generated by _cython_wrapper_generators.py.\n",
               "# Do not edit this file directly.\n\n"]
    with open(outfile, 'w') as f:
        f.writelines(comment)
        f.writelines(signatures)

# The signature that is used for zcgesv in lapack 3.1.0 and 3.1.1 changed
# in version 3.2.0. The version included in the clapack on OSX has the
# more recent signature though.
# slamch and dlamch are not in the lapack src directory, but,since they
# already have Python wrappers, we'll wrap them as well.
# The other manual signatures are used because the signature generating
# functions don't work when function pointer arguments are used.

lapack_manual_wrappers = '''void cgees(char *jobvs, char *sort, cselect1 *select, int *n, c *a, int *lda, int *sdim, c *w, c *vs, int *ldvs, c *work, int *lwork, s *rwork, bint *bwork, int *info)
void cgeesx(char *jobvs, char *sort, cselect1 *select, char *sense, int *n, c *a, int *lda, int *sdim, c *w, c *vs, int *ldvs, s *rconde, s *rcondv, c *work, int *lwork, s *rwork, bint *bwork, int *info)
void cgges(char *jobvsl, char *jobvsr, char *sort, cselect2 *selctg, int *n, c *a, int *lda, c *b, int *ldb, int *sdim, c *alpha, c *beta, c *vsl, int *ldvsl, c *vsr, int *ldvsr, c *work, int *lwork, s *rwork, bint *bwork, int *info)
void cggesx(char *jobvsl, char *jobvsr, char *sort, cselect2 *selctg, char *sense, int *n, c *a, int *lda, c *b, int *ldb, int *sdim, c *alpha, c *beta, c *vsl, int *ldvsl, c *vsr, int *ldvsr, s *rconde, s *rcondv, c *work, int *lwork, s *rwork, int *iwork, int *liwork, bint *bwork, int *info)
void dgees(char *jobvs, char *sort, dselect2 *select, int *n, d *a, int *lda, int *sdim, d *wr, d *wi, d *vs, int *ldvs, d *work, int *lwork, bint *bwork, int *info)
void dgeesx(char *jobvs, char *sort, dselect2 *select, char *sense, int *n, d *a, int *lda, int *sdim, d *wr, d *wi, d *vs, int *ldvs, d *rconde, d *rcondv, d *work, int *lwork, int *iwork, int *liwork, bint *bwork, int *info)
void dgges(char *jobvsl, char *jobvsr, char *sort, dselect3 *selctg, int *n, d *a, int *lda, d *b, int *ldb, int *sdim, d *alphar, d *alphai, d *beta, d *vsl, int *ldvsl, d *vsr, int *ldvsr, d *work, int *lwork, bint *bwork, int *info)
void dggesx(char *jobvsl, char *jobvsr, char *sort, dselect3 *selctg, char *sense, int *n, d *a, int *lda, d *b, int *ldb, int *sdim, d *alphar, d *alphai, d *beta, d *vsl, int *ldvsl, d *vsr, int *ldvsr, d *rconde, d *rcondv, d *work, int *lwork, int *iwork, int *liwork, bint *bwork, int *info)
d dlamch(char *cmach)
void ilaver(int *vers_major, int *vers_minor, int *vers_patch)
void sgees(char *jobvs, char *sort, sselect2 *select, int *n, s *a, int *lda, int *sdim, s *wr, s *wi, s *vs, int *ldvs, s *work, int *lwork, bint *bwork, int *info)
void sgeesx(char *jobvs, char *sort, sselect2 *select, char *sense, int *n, s *a, int *lda, int *sdim, s *wr, s *wi, s *vs, int *ldvs, s *rconde, s *rcondv, s *work, int *lwork, int *iwork, int *liwork, bint *bwork, int *info)
void sgges(char *jobvsl, char *jobvsr, char *sort, sselect3 *selctg, int *n, s *a, int *lda, s *b, int *ldb, int *sdim, s *alphar, s *alphai, s *beta, s *vsl, int *ldvsl, s *vsr, int *ldvsr, s *work, int *lwork, bint *bwork, int *info)
void sggesx(char *jobvsl, char *jobvsr, char *sort, sselect3 *selctg, char *sense, int *n, s *a, int *lda, s *b, int *ldb, int *sdim, s *alphar, s *alphai, s *beta, s *vsl, int *ldvsl, s *vsr, int *ldvsr, s *rconde, s *rcondv, s *work, int *lwork, int *iwork, int *liwork, bint *bwork, int *info)
s slamch(char *cmach)
void zgees(char *jobvs, char *sort, zselect1 *select, int *n, z *a, int *lda, int *sdim, z *w, z *vs, int *ldvs, z *work, int *lwork, d *rwork, bint *bwork, int *info)
void zgeesx(char *jobvs, char *sort, zselect1 *select, char *sense, int *n, z *a, int *lda, int *sdim, z *w, z *vs, int *ldvs, d *rconde, d *rcondv, z *work, int *lwork, d *rwork, bint *bwork, int *info)
void zgges(char *jobvsl, char *jobvsr, char *sort, zselect2 *selctg, int *n, z *a, int *lda, z *b, int *ldb, int *sdim, z *alpha, z *beta, z *vsl, int *ldvsl, z *vsr, int *ldvsr, z *work, int *lwork, d *rwork, bint *bwork, int *info)
void zggesx(char *jobvsl, char *jobvsr, char *sort, zselect2 *selctg, char *sense, int *n, z *a, int *lda, z *b, int *ldb, int *sdim, z *alpha, z *beta, z *vsl, int *ldvsl, z *vsr, int *ldvsr, d *rconde, d *rcondv, z *work, int *lwork, d *rwork, int *iwork, int *liwork, bint *bwork, int *info)'''

if __name__ == '__main__':
    from sys import argv
    libname, src_dir, outfile = argv[1:]
    # Exclude scabs and sisnan since they aren't currently included
    # in the scipy-specific ABI wrappers.
    if libname.lower() == 'blas':
        sigs_from_dir(src_dir, outfile, exclusions=['scabs1', 'xerbla'])
    elif libname.lower() == 'lapack':
        # Exclude all routines that do not have consistent interfaces from
        # LAPACK 3.1.0 through 3.5.0.
        # Also exclude routines with string arguments to avoid
        # compatibility woes with different standards for string arguments.
        # Exclude sisnan and slaneg since they aren't currently included in
        # The ABI compatibility wrappers.
        exclusions = ['sisnan', 'csrot', 'zdrot', 'ilaenv', 'iparmq', 'lsamen',
                      'xerbla', 'zcgesv', 'dlaisnan', 'slaisnan', 'dlazq3',
                      'dlazq4', 'slazq3', 'slazq4', 'dlasq3', 'dlasq4',
                      'slasq3', 'slasq4', 'dlasq5', 'slasq5', 'slaneg']
        sigs_from_dir(src_dir, outfile, manual_wrappers=lapack_manual_wrappers,
                      exclusions=exclusions)