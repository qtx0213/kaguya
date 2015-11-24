def args(out,arg_num,name,argoffset=0):
	if arg_num > 0:
		for i in range (argoffset,arg_num):
			if i > argoffset:
				out.write(',')
			out.write(name + str(i+1))

def func(out,rettype,arg_num):
	out.write('  typedef '+ rettype +' (*func_type)(')
	args(out,arg_num,'T');
	out.write(') ;\n')
	out.write('  func_type func_;\n')

def function_func(out,rettype,arg_num):
	out.write('  typedef standard::function<'+ rettype +'(')
	args(out,arg_num,'T');
	out.write(')> func_type;\n')
	out.write('  func_type func_;\n')

def mem_func(out,rettype,arg_num,funattr):
	out.write('  typedef '+ rettype +' (T1::*func_type)')
	out.write('(')
	args(out,arg_num+1,'T',1);
	out.write(') ' + funattr + ';\n')
	out.write('  func_type func_;\n')

def template(out,arg_num):
	out.write('template<typename Ret')
	if arg_num > 0:
		out.write(',')
		args(out,arg_num,'typename T')
	out.write('>\n')

def void_template(out,arg_num):
	if arg_num > 0:
		out.write('template<')
		args(out,arg_num,'typename T')
		out.write('>\n')

def get_call(out,arg_num,offset=0):
	for i in range (offset + 1,arg_num + 1):
		out.write('    T'+str(i) +' t' +str(i) +' = types::get(state,' + str(i) + ',types::type_tag<T'+ str(i) + '>());\n')

def arg_types_string(out,arg_num):
	out.write('std::string()')
	for i in range (arg_num):
		if i>0:
			out.write('+ ","')
		out.write('+ typeid(T' + str(i+1) + ').name()')


	
def strict_check_type(out,arg_num,offset=0,customcheck=""):
	out.write('  virtual bool checktype(lua_State *state,bool strictcheck){\n')
	out.write('    if(lua_gettop(state) != ' + str(arg_num) + '){return false;}\n')
	
	out.write(customcheck)
	out.write('    if(strictcheck){\n')
	out.write('      if(false')
	for i in range (offset+1,arg_num+1):
		out.write('|| !types::strict_check_type(state,' + str(i) + ',types::type_tag<T'+ str(i) + '>())')
	out.write('){return false;}\n')
	out.write('  }else{\n')	
	out.write('      if(false')
	for i in range (offset+1,arg_num+1):
		out.write('|| !types::check_type(state,' + str(i) + ',types::type_tag<T'+ str(i) + '>())')
	out.write('){return false;}\n')
	out.write('  }\n')
	out.write('    return true;\n')
	out.write('  }\n')


def standard_function(out,arg_num):
	basename = 'baseInvoker'
	classname = 'function_caller' + str(arg_num)

	template(out,arg_num)
	out.write('struct ' + classname + ':' + basename)
	out.write('{\n')
	function_func(out,'Ret',arg_num)

	out.write('  ' + classname + '(func_type fun):func_(fun){}\n')

	strict_check_type(out,arg_num)
	out.write('  virtual int invoke(lua_State *state)\n')
	out.write('  {\n')

	get_call(out,arg_num)

	out.write('    Ret r = func_(')
	args(out,arg_num,'t')
	out.write(');\n')
	out.write('    return types::push(state,standard::forward<Ret>(r));\n')
	out.write('  }\n')
	out.write('};\n')

	template(out,arg_num)
	out.write('baseInvoker* create(standard::function<Ret (')
	args(out,arg_num,'T');

	out.write(')> fun)\n')
	out.write('{\n')

	out.write('  typedef ' + classname +'<Ret')

	if arg_num > 0:
		out.write(',')
		args(out,arg_num,'T')
	out.write('> caller_type;\n');
	
	out.write('  return new caller_type(fun);\n')
	out.write('}\n')


def void_standard_function(out,arg_num):
	basename = 'baseInvoker'
	classname = 'void_function_caller' + str(arg_num)

	void_template(out,arg_num)
	out.write('struct ' + classname + ':' + basename)
	out.write('{\n')

	function_func(out,'void',arg_num)

	#constructor
	out.write('  ' + classname + '(func_type fun):func_(fun){}\n')

	strict_check_type(out,arg_num)
	
	out.write('  virtual int invoke(lua_State *state)\n')
	out.write('  {\n')

	get_call(out,arg_num)

	out.write('    func_(')
	args(out,arg_num,'t')
	out.write(');\n')
	out.write('    return 0;\n')
	out.write('  }\n')
	out.write('};\n')

	void_template(out,arg_num)
	out.write('baseInvoker* create(standard::function<void (')
	args(out,arg_num,'T');

	out.write(')> fun)\n')
	out.write('{\n')
	
	out.write('  typedef '+classname)
	if arg_num > 0:
		out.write('<')
		args(out,arg_num,'T')
		out.write('>')
	out.write(' caller_type;\n');

	out.write('  return new caller_type(fun);\n')
	out.write('}\n')


def tepmlate_function(out,arg_num):
	basename = 'baseInvoker'
	classname = 'caller' + str(arg_num)

	template(out,arg_num)
	out.write('struct ' + classname + ':' + basename)
	out.write('{\n')
	func(out,'Ret',arg_num)


	out.write('  ' + classname + '(func_type fun):func_(fun){}\n')

	strict_check_type(out,arg_num)
	
	out.write('  virtual int invoke(lua_State *state)\n')
	out.write('  {\n')

	get_call(out,arg_num)

	out.write('    Ret r = func_(')
	args(out,arg_num,'t')
	out.write(');\n')
	out.write('    return types::push(state,standard::forward<Ret>(r));\n')
	out.write('  }\n')
	out.write('};\n')

	template(out,arg_num)
	out.write('baseInvoker* create(Ret (*fun)(')
	args(out,arg_num,'T');

	out.write('))\n')
	out.write('{\n')

	out.write('  typedef ' +classname+'<Ret')

	if arg_num > 0:
		out.write(',')
		args(out,arg_num,'T')
	out.write('> caller_type;\n');
	
	out.write('  return new caller_type(fun);\n')
	out.write('}\n')

def void_tepmlate_function(out,arg_num):
	basename = 'baseInvoker'
	classname = 'void_caller' + str(arg_num)

	void_template(out,arg_num)
	out.write('struct ' + classname + ':' + basename)
	out.write('{\n')

	func(out,'void',arg_num)

	out.write('  ' + classname + '(func_type fun):func_(fun){}')

	strict_check_type(out,arg_num)
	
	out.write('  virtual int invoke(lua_State *state)\n')
	out.write('  {\n')

	get_call(out,arg_num)

	out.write('    func_(')
	args(out,arg_num,'t')
	out.write(');\n')
	out.write('    return 0;\n')
	out.write('  }\n')
	out.write('};\n')


	void_template(out,arg_num)
	out.write('baseInvoker* create(void (*fun)(')
	args(out,arg_num,'T');

	out.write('))\n')
	out.write('{\n')
	
	out.write('  typedef ' + classname)
	if arg_num > 0:
		out.write('<')
		args(out,arg_num,'T')
		out.write('>')
	out.write(' caller_type;\n');

	out.write('  return new caller_type(fun);\n')
	out.write('}\n')


def tepmlate_mem_function(out,arg_num,funattr):
	basename = 'baseInvoker'
	classname = funattr+'mem_caller' + str(arg_num)

	template(out,arg_num + 1)
	out.write('struct ' + classname + ':' + basename)
	out.write('{\n')
	mem_func(out,'Ret',arg_num,funattr)

	out.write('  ' + classname + '(func_type fun):func_(fun){}\n')

	strict_check_type(out,arg_num+1,1,'if(getPtr(state) == 0){return false;}\n')
	
	out.write('  T1* getPtr(lua_State *state) {\n')
	out.write('    if (types::check_type(state, 1, types::type_tag<T1*>()))\n')
	out.write('    {\n')
	out.write('      return types::get(state, 1, types::type_tag<T1*>());\n')
	out.write('   }\n')
	out.write('   if (types::check_type(state, 1, types::type_tag<standard::shared_ptr<T1>*>()))\n')
	out.write('    {\n')
	out.write('      standard::shared_ptr<T1>* shared_ptr = types::get(state, 1, types::type_tag<standard::shared_ptr<T1>*>());\n')
	out.write('      if (shared_ptr) {\n')
	out.write('        return shared_ptr->get();\n')
	out.write('      }\n')
	out.write('    }\n')
	out.write('    return 0;\n')
	out.write('  }\n')
	
	out.write('  virtual int invoke(lua_State *state)\n')
	out.write('  {\n')

	get_call(out,arg_num+1,1)
	
	
	out.write('  T1* ptr = getPtr(state);\n')
	
	out.write('    Ret r = (ptr->*func_)(')
	args(out,arg_num+1,'t',1)
	out.write(');\n')
	out.write('    return types::push(state,standard::forward<Ret>(r));\n')
	out.write('  }\n')
	out.write('};\n')

	template(out,arg_num + 1)
	out.write('baseInvoker* create(Ret (T1::*fun)(')
	args(out,arg_num+1,'T',1);

	out.write(')' +funattr + ')\n')
	out.write('{\n')

	out.write('  typedef ' + classname+'<Ret,')
	args(out,arg_num+1,'T')
	out.write('> caller_type;\n');
	
	out.write('  return new caller_type(fun);\n')
	out.write('}\n')

def void_tepmlate_mem_function(out,arg_num,funattr):
	basename = 'baseInvoker'
	classname = funattr+'void_mem_caller' + str(arg_num)

	void_template(out,arg_num+1)
	out.write('struct ' + classname + ':' + basename)
	out.write('{\n')

	mem_func(out,'void',arg_num,funattr)


	out.write('  ' + classname + '(func_type fun):func_(fun){}\n')

	strict_check_type(out,arg_num+1,1,'if(getPtr(state) == 0){return false;}\n')
	
	out.write('  T1* getPtr(lua_State *state) {\n')
	out.write('    if (types::check_type(state, 1, types::type_tag<T1*>()))\n')
	out.write('    {\n')
	out.write('      return types::get(state, 1, types::type_tag<T1*>());\n')
	out.write('   }\n')
	out.write('   if (types::check_type(state, 1, types::type_tag<standard::shared_ptr<T1>*>()))\n')
	out.write('    {\n')
	out.write('      standard::shared_ptr<T1>* shared_ptr = types::get(state, 1, types::type_tag<standard::shared_ptr<T1>*>());\n')
	out.write('      if (shared_ptr) {\n')
	out.write('        return shared_ptr->get();\n')
	out.write('      }\n')
	out.write('    }\n')
	out.write('    return 0;\n')
	out.write('  }\n')
	
	out.write('  virtual int invoke(lua_State *state)\n')
	out.write('  {\n')


	get_call(out,arg_num+1,1)
	out.write('  T1* ptr = getPtr(state);\n')
	out.write('    (ptr->*func_)(')
	args(out,arg_num+1,'t',1)
	out.write(');\n')
	out.write('    return 0;\n')
	out.write('  }\n')
	out.write('};\n')

	void_template(out,arg_num+1)
	out.write('baseInvoker* create(void (T1::*fun)(')
	args(out,arg_num+1,'T',1);

	out.write(')'+ funattr +')\n')
	out.write('{\n')
	

	out.write('  typedef ' + classname+'<')
	args(out,arg_num+1,'T')
	out.write('> caller_type;\n');

	out.write('  return new caller_type(fun);\n')
	out.write('}\n')


def constructor_function(out,arg_num):
	basename = 'baseInvoker'
	classname = 'constructor_caller' + str(arg_num)

	out.write('template<typename CLASS')
	if arg_num > 0:
		out.write(',')
		args(out,arg_num,'typename T')
	out.write('>\n')
	out.write('struct ' + classname + ':' + basename)
	out.write('{\n')


	out.write('  ' + classname + '(){}\n')

	strict_check_type(out,arg_num)
	
	out.write('  virtual int invoke(lua_State *state)\n')
	out.write('  {\n')

	get_call(out,arg_num)
	out.write('  void *storage = lua_newuserdata(state, sizeof(CLASS));\n')


	out.write('    CLASS* ptr = types::constructor<CLASS>(storage')
	if arg_num > 0:
		out.write(',')
		args(out,arg_num,'t')
	out.write(');\n')
	out.write('    luaL_setmetatable(state, types::metatable_name<CLASS>().c_str());\n')
	out.write('    return 1;\n')
	out.write('  }\n')
	out.write('};\n')


if __name__ == '__main__':
	import sys
	sys.stdout.write('//generated header by ' + __file__ + "\n")
	for i in range(10):
		standard_function(sys.stdout,i)
	for i in range(10):
		void_standard_function(sys.stdout,i)
	for i in range(10):
		tepmlate_function(sys.stdout,i)
	for i in range(10):
		void_tepmlate_function(sys.stdout,i)
	for i in range(10):
		tepmlate_mem_function(sys.stdout,i,"")
		tepmlate_mem_function(sys.stdout,i,"const")
	for i in range(10):
		void_tepmlate_mem_function(sys.stdout,i,"")
		void_tepmlate_mem_function(sys.stdout,i,"const")
	for i in range(10):
		constructor_function(sys.stdout,i)
