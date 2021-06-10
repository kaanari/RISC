library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity SignExtent is

	generic(
				DATA_WIDTH 	: integer := 16				
	);

	port(
			Input:	in std_logic_vector(7 downto 0);
			Output:	out std_logic_vector((DATA_WIDTH-1) downto 0)	
	);


end SignExtent;

architecture dataflow of SignExtent is
begin

	Output(7 downto 0) <= Input;
	Output((DATA_WIDTH-1) downto 8) <= (others => Input(7));

end dataflow;  