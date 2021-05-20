library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

entity OpcodeDecoder_tb is
end OpcodeDecoder_tb;

architecture testbench of OpcodeDecoder_tb is
	 
	
	component OpcodeDecoder is

		port(
				OpCode : in std_logic_vector(3 downto 0);
				Operation : out std_logic_vector(15 downto 0)	
		);


	end component;

	
	signal OpCode 		: std_logic_vector(3 downto 0)  := (others => '0');
	signal Operation 	: std_logic_vector(15 downto 0)  := (others => '0');
	signal opTemp  	: std_logic_vector(15 downto 0)  := (others => '0'); 

begin
	
	
	UUT: OpcodeDecoder port map(OpCode, Operation);
	Stimulus: process
	
	begin
		
		for i in 0 to 15 loop
		
			OpCode 	 <= std_logic_vector(to_unsigned(i,OpCode'length));
			opTemp	 <= (others => '0');
			opTemp(i) <= '1';
			
			wait for 50 ps;
			
			assert Operation = opTemp
			report "There are error in  "& integer'image(i)& " !" 
			severity error;
			
			wait for 50 ps;
		
		end loop;
		
		wait;
		
	end process;
	

end testbench;