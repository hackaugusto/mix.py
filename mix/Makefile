# PYTHON_VERSION = 3.5m
PYTHON_VERSION = 2.7
PYTHON_INCLUDE = /usr/include/python$(PYTHON_VERSION)

BOOST_INC = /usr/include
BOOST_LIB = /usr/lib

# CXX = clang
CXX = gcc
CXXFLAGS = -ggdb3 -Wall -Wextra -Werror -Wno-long-long -Wno-variadic-macros -fexceptions -DNDEBUG -std=c++14 -pipe -fstack-protector-strong --param=ssp-buffer-size=4
LDFLAGS = -Wl,-O1,--sort-common,--as-needed,-z,relro,--export-dynamic
INCLUDES = -I . -I ${BOOST_INC} -I $(PYTHON_INCLUDE)
# LIBS = -L$(BOOST_LIB) -L/usr/lib/python$(PYTHON_VERSION)/config -lpython3 -lboost_python3 -lboost_context
LIBS = -L$(BOOST_LIB) -L/usr/lib/python$(PYTHON_VERSION)/config -lpython2.7 -lboost_python -lboost_context

TARGET = fiber

$(TARGET).so: $(TARGET).o
	$(CXX) $(CXXFLAGS) $(INCLUDES) $(LIBS) -shared $(LDFLAGS) $(TARGET).o -o $(TARGET).so

$(TARGET).o: $(TARGET).cpp
	$(CXX) $(CXXFLAGS) $(INCLUDES) -fPIC -c $(TARGET).cpp

# python setup.py clean leaves most of it behind (dist, the build dir, and libraries from develop command)
clean:
	rm *.so *.o || true
	# rm compile_commands.json || true
	# rm -r build mix.py.egg-info .tox || true
