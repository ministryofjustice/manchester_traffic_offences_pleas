class SitePrismSubclass
  class << self
    attr_accessor :results
    def <<(input)
      @results ||= {}
      @results[input.to_s.demodulize.underscore] = input
      @results
    end
  end
end
