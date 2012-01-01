%w{ rubygems rake }.each { |pack| require pack }

module Dependencies
  %w{python pip virtualenv nosetests pylint git}.each do |dep|
    define_method(dep) do |input = nil|
      sh "#{dep} #{Array === input ? input.join(' ') : input}"
    end
  end

  self
end

module Support
  def background(cmd)
    pid = fork { exec(cmd) }
    Process.detach(pid)

    sleep 5 and yield

    Process.kill("TERM", pid)
  end

  def bench(path, message)
    # The command below is based on the express benchmark.
    system <<-CMD
      ab -n 5000 -c 50 -k -q http://127.0.0.1:8088#{path} \
        | grep "Requests per" \
        | cut -d ' ' -f 7 \
        | xargs echo "#{message}:"
    CMD
  end
end

[FileUtils, Dependencies, Support].each { |mod| include mod }

desc "Cleans all"
task :clean => (namespace :clean do
  desc "Cleans the VIM leftouvers"
  task :vim do
    Dir['**/.*.sw?'].each { |file| rm file }
  end

  desc "Cleans the Python bytecode leftouvers"
  task :py do
    Dir['**/*.py[co]'].each { |file| rm file }
  end
end).tasks

desc "Runs pylint"
task(:lint) { pylint ["-E", "plush"] }

desc "Runs the tests"
task(:test) { nosetests "test" }

desc "Runs the benchmarks"
task :bench do
  background 'python support/plushapp.py' do
    bench '/', 'Plush' 
  end

  background 'python support/tornadoapp.py' do
    bench '/', 'Tornado'
  end
end

namespace :git do
  desc "Adds all of the current files under git"
  task :add_files => [:clean] do
    sh "find . | grep -v '.git' | xargs git add"
  end
end

task :default => [:clean, :test]
