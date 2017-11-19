#!/usr/bin/env python
#
# __COPYRIGHT__
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os
import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.write('myjar.py', r"""
import sys
args = sys.argv[1:]
while args:
    a = args[0]
    if a == 'cf':
        out = args[1]
        args = args[1:]
    else:
        break
    args = args[1:]
outfile = open(out, 'w')
for file in args:
    infile = open(file, 'r')
    for l in infile.readlines():
        if l[:7] != '/*jar*/':
            outfile.write(l)
sys.exit(0)
""")

test.write('SConstruct', """
env = Environment(tools = ['jar'],
                  JAR = r'%(_python_)s myjar.py')
env.Jar(target = 'test1.jar', source = 'test1.class')
""" % locals())

test.write('test1.class', """\
test1.class
/*jar*/
line 3
""")

test.run(arguments='.', stderr=None)

test.must_match('test1.jar', "test1.class\nline 3\n", mode='r')

if os.path.normcase('.class') == os.path.normcase('.CLASS'):

    test.write('SConstruct', """
env = Environment(tools = ['jar'],
                  JAR = r'%(_python_)s myjar.py')
env.Jar(target = 'test2.jar', source = 'test2.CLASS')
""" % locals())

    test.write('test2.CLASS', """\
test2.CLASS
/*jar*/
line 3
""")

    test.run(arguments='.', stderr=None)

    test.must_match('test2.jar', "test2.CLASS\nline 3\n", mode='r')

test.write('myjar2.py', r"""
import sys
f=open(sys.argv[2], 'w')
f.write(" ".join(sys.argv[1:]))
f.write("\n")
f.close()
sys.exit(0)
""")

test.write('SConstruct', """
env = Environment(tools = ['jar'],
                  JAR = r'%(_python_)s myjar2.py',
                  JARFLAGS='cvf')
env.Jar(target = 'classes.jar', source = [ 'testdir/bar.class',
                                           'foo.mf' ],
        TESTDIR='testdir',
        JARCHDIR='$TESTDIR')
""" % locals())

test.subdir('testdir')
test.write(['testdir', 'bar.class'], 'foo')
test.write('foo.mf',
           """Manifest-Version : 1.0
           blah
           blah
           blah
           """)
test.run(arguments='classes.jar')
test.must_match('classes.jar',
                'cvfm classes.jar foo.mf -C testdir bar.class\n', mode='r')



where_javac, java_version = test.java_where_javac()
where_jar = test.java_where_jar()



test.file_fixture('wrapper_with_args.py')

test.write('SConstruct', """
foo = Environment(tools = ['javac', 'jar'],
                  JAVAC = r'%(where_javac)s',
                  JAR = r'%(where_jar)s')
jar = foo.Dictionary('JAR')
bar = foo.Clone(JAR = r'%(_python_)s wrapper_with_args.py ' + jar)
foo.Java(target = 'classes', source = 'com/sub/foo')
bar.Java(target = 'classes', source = 'com/sub/bar')
foo.Jar(target = 'foo', source = 'classes/com/sub/foo')
bar.Jar(target = 'bar', source = 'classes/com/sub/bar')
""" % locals())

test.subdir('com',
            ['com', 'sub'],
            ['com', 'sub', 'foo'],
            ['com', 'sub', 'bar'])

test.write(['com', 'sub', 'foo', 'Example1.java'], """\
package com.sub.foo;

public class Example1
{

     public static void main(String[] args)
     {

     }

}
""")

test.write(['com', 'sub', 'foo', 'Example2.java'], """\
package com.sub.foo;

public class Example2
{

     public static void main(String[] args)
     {

     }

}
""")

test.write(['com', 'sub', 'foo', 'Example3.java'], """\
package com.sub.foo;

public class Example3
{

     public static void main(String[] args)
     {

     }

}
""")

test.write(['com', 'sub', 'bar', 'Example4.java'], """\
package com.sub.bar;

public class Example4
{

     public static void main(String[] args)
     {

     }

}
""")

test.write(['com', 'sub', 'bar', 'Example5.java'], """\
package com.sub.bar;

public class Example5
{

     public static void main(String[] args)
     {

     }

}
""")

test.write(['com', 'sub', 'bar', 'Example6.java'], """\
package com.sub.bar;

public class Example6
{

     public static void main(String[] args)
     {

     }

}
""")

test.run(arguments = '.')

expected_wrapper_out = "wrapper_with_args.py %(where_jar)s cf bar.jar classes/com/sub/bar\n"
expected_wrapper_out = expected_wrapper_out.replace('/', os.sep)
test.must_match('wrapper.out',
                expected_wrapper_out % locals(), mode='r')

test.must_exist('foo.jar')
test.must_exist('bar.jar')

test.up_to_date(arguments = '.')

#######
# test java source files as source to Jar builder

# make some directories to test in
test.subdir('testdir2',
            ['testdir2', 'com'],
            ['testdir2', 'com', 'javasource'])

# simple SConstruct which passes the 3 .java as source
# and extracts the jars back to classes
test.write(['testdir2', 'SConstruct'], """
foo = Environment()
foo.Jar(target = 'foobar', source = [
    'com/javasource/JavaFile1.java', 
    'com/javasource/JavaFile2.java',
    'com/javasource/JavaFile3.java'
])
foo.Jar(target = ['foo', 'bar'], source = [
    'com/javasource/JavaFile1.java', 
    'com/javasource/JavaFile2.java',
    'com/javasource/JavaFile3.java'
])
foo.Command("foobarTest", [], Mkdir("foobarTest") )
foo.Command('foobarTest/com/javasource/JavaFile3.java', 'foobar.jar', foo['JAR'] + ' xvf ../foobar.jar', chdir='foobarTest')
foo.Command("fooTest", [], Mkdir("fooTest") )
foo.Command('fooTest/com/javasource/JavaFile3.java', 'foo.jar', foo['JAR'] + ' xvf ../foo.jar', chdir='fooTest')
foo.Command("barTest", [], Mkdir("barTest") )
foo.Command('barTest/com/javasource/JavaFile3.java', 'bar.jar', foo['JAR'] + ' xvf ../bar.jar', chdir='barTest')
""")

test.write(['testdir2', 'com', 'javasource', 'JavaFile1.java'], """\
package com.javasource;

public class JavaFile1
{
     public static void main(String[] args)
     {

     }
}
""")

test.write(['testdir2', 'com', 'javasource', 'JavaFile2.java'], """\
package com.javasource;

public class JavaFile2
{
     public static void main(String[] args)
     {

     }
}
""")

test.write(['testdir2', 'com', 'javasource', 'JavaFile3.java'], """\
package com.javasource;

public class JavaFile3
{
     public static void main(String[] args)
     {

     }
}
""")

test.run(chdir='testdir2')

# check the output and make sure the java files got converted to classes
if("jar cf foo.jar " +
   "-C com/javasource/JavaFile1 com/javasource/JavaFile1.class " +
   "-C com/javasource/JavaFile2 com/javasource/JavaFile2.class " +
   "-C com/javasource/JavaFile3 com/javasource/JavaFile3.class" not in test.stdout()):
    test.fail_test()

#test single target jar
test.must_exist(['testdir2','foobar.jar'])
test.must_exist(['testdir2', 'foobarTest', 'com', 'javasource', 'JavaFile1.class'])
test.must_exist(['testdir2', 'foobarTest', 'com', 'javasource', 'JavaFile2.class'])
test.must_exist(['testdir2', 'foobarTest', 'com', 'javasource', 'JavaFile3.class'])

# make sure there are class in the jar
test.must_exist(['testdir2','foo.jar'])
test.must_exist(['testdir2', 'fooTest', 'com', 'javasource', 'JavaFile1.class'])
test.must_exist(['testdir2', 'fooTest', 'com', 'javasource', 'JavaFile2.class'])
test.must_exist(['testdir2', 'fooTest', 'com', 'javasource', 'JavaFile3.class'])

# make sure both jars got createds
test.must_exist(['testdir2','bar.jar'])
test.must_exist(['testdir2', 'barTest', 'com', 'javasource', 'JavaFile1.class'])
test.must_exist(['testdir2', 'barTest', 'com', 'javasource', 'JavaFile2.class'])
test.must_exist(['testdir2', 'barTest', 'com', 'javasource', 'JavaFile3.class'])


#######
# test list of lists

# make some directories to test in
test.subdir('listOfLists',
            ['listOfLists', 'src'],
            ['listOfLists', 'src', 'com'],
            ['listOfLists', 'src', 'com', 'javasource'],
            ['listOfLists', 'src', 'com', 'resource'])

# simple SConstruct which passes the 3 .java as source
# and extracts the jars back to classes
test.write(['listOfLists', 'SConstruct'], """
foo = Environment()
list_of_class_files = foo.Java('src', source=['src'])
resources = ['src/com/resource/resource1.txt', 'src/com/resource/resource2.txt']
contents = [list_of_class_files, resources]
foo.Jar(target = 'lists', source = contents + ['MANIFEST.mf'], JARCHDIR='src')
foo.Command("listsTest", [], Mkdir("listsTest") )
foo.Command('listsTest/src/com/javasource/JavaFile3.java', 'lists.jar', foo['JAR'] + ' xvf ../lists.jar', chdir='listsTest')
""")

test.write(['listOfLists', 'src', 'com', 'javasource', 'JavaFile1.java'], """\
package com.javasource;

public class JavaFile1
{
     public static void main(String[] args)
     {

     }
}
""")

test.write(['listOfLists', 'src', 'com', 'javasource', 'JavaFile2.java'], """\
package com.javasource;

public class JavaFile2
{
     public static void main(String[] args)
     {

     }
}
""")

test.write(['listOfLists', 'src', 'com', 'javasource', 'JavaFile3.java'], """\
package com.javasource;

public class JavaFile3
{
     public static void main(String[] args)
     {

     }
}
""")

test.write(['listOfLists', 'MANIFEST.mf'],
"""Manifest-Version: 1.0
MyManifestTest: Test
""")

test.write(['listOfLists', 'src', 'com', 'resource', 'resource1.txt'], """\
this is a resource file
""")

test.write(['listOfLists', 'src', 'com', 'resource', 'resource2.txt'], """\
this is another resource file
""")


test.run(chdir='listOfLists')

#test single target jar
test.must_exist(['listOfLists','lists.jar'])

# make sure there are class in the jar
test.must_exist(['listOfLists', 'listsTest', 'com', 'javasource', 'JavaFile1.class'])
test.must_exist(['listOfLists', 'listsTest', 'com', 'javasource', 'JavaFile2.class'])
test.must_exist(['listOfLists', 'listsTest', 'com', 'javasource', 'JavaFile3.class'])
test.must_exist(['listOfLists', 'listsTest', 'com', 'resource', 'resource1.txt'])
test.must_exist(['listOfLists', 'listsTest', 'com', 'resource', 'resource2.txt'])
test.must_exist(['listOfLists', 'listsTest', 'META-INF', 'MANIFEST.MF'])
test.must_contain(['listOfLists', 'listsTest', 'META-INF', 'MANIFEST.MF'], b"MyManifestTest: Test" )
test.pass_test()


# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
