RUNDIR=`pwd`
cd `dirname $0`
MYDIR=`pwd`
ROOT=${MYDIR}/../..
ENV=.env.36
SRC=${ROOT}/sic
DIST=${ROOT}/dist
TEST=${ROOT}/test
cd ${ROOT}
rm -r ${ROOT}/build
rm -r ${ROOT}/cythonized
mkdir -p ${ROOT}/dist
${ROOT}/${ENV}/bin/python3 ${TEST}/compile.py build_ext --inplace
mv ${ROOT}/*.so ${ROOT}/dist
cd ${RUNDIR}
